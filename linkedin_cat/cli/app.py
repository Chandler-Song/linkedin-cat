"""
LinkedIn Cat CLI 主入口
Typer + Rich 命令行界面
"""

import typer
import time
import random
import logging
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, 
    BarColumn, TaskProgressColumn, TimeRemainingColumn
)
from rich.prompt import Confirm
from pathlib import Path
from typing import Optional
from datetime import datetime

from linkedin_cat.config import LinkedinCatConfig
from linkedin_cat.cache import ContactCache
from linkedin_cat.wrapper import LinkedInClient, SendResult
from linkedin_cat.utils import replace_template_variables, normalize_url

# 创建 Typer 应用
app = typer.Typer(
    name="linkedincat",
    help="🐱 LinkedIn Cat - LinkedIn 自动化工具",
    add_completion=True,
    rich_markup_mode="rich"
)
console = Console()

# 确保日志目录存在
Path("logs").mkdir(exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/linkedincat.log", encoding="utf-8")]
)


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细日志"),
    config_path: Path = typer.Option("config.yaml", "--config", "-c", help="配置文件路径")
):
    """
    🐱 LinkedIn Cat - 基于 Selenium 的 LinkedIn 自动化工具
    
    支持消息发送、搜索、档案抓取等功能，提供企业级的稳定性和可靠性。
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@app.command()
def init():
    """
    🚀 初始化工作目录和示例文件
    
    创建必要的目录结构和示例配置文件。
    """
    dirs = ["message", "urls", "cache", "logs"]
    
    with console.status("[bold green]初始化 LinkedIn Cat 工作区...") as status:
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
            status.update(f"[bold green]创建 {d}/")
        
        # 创建默认配置
        config = LinkedinCatConfig.from_yaml()
        console.print(f"[green]✓[/green] 配置: config.yaml")
        
        # 创建示例消息模板
        msg_default = Path("message/default.txt")
        if not msg_default.exists():
            msg_default.write_text("""Hi there,

I came across your profile and was impressed by your background.

I'd love to connect and explore potential synergies between our work.

Best regards,
[Your Name]
""", encoding='utf-8')
            console.print(f"[green]✓[/green] 模板: message/default.txt")
        
        # 招聘模板
        msg_recruit = Path("message/recruitment.txt")
        if not msg_recruit.exists():
            msg_recruit.write_text("""Hi {{name|there}},

I'm {{sender|a recruiter}} at {{company|a tech firm}}. Your experience in {{field|software development}} caught my attention.

We're hiring for {{role|Senior Developer}} - would you be open to a brief chat?

Best,
{{sender|HR Team}}
""", encoding='utf-8')
            console.print(f"[green]✓[/green] 模板: message/recruitment.txt")
        
        # 创建示例 URL 列表
        urls_demo = Path("urls/demo.txt")
        if not urls_demo.exists():
            urls_demo.write_text("""# 每行一个 LinkedIn 个人主页 URL
# 删除这些示例行，添加真实 URL

https://www.linkedin.com/in/williamhgates/
https://www.linkedin.com/in/satyanadella/
""", encoding='utf-8')
            console.print(f"[green]✓[/green] 列表: urls/demo.txt")
    
    console.print(Panel.fit(
        "[bold green]🐱 LinkedIn Cat 初始化完成！[/bold green]\n\n"
        "[yellow]下一步：[/yellow]\n"
        "1. 编辑 [cyan]config.yaml[/cyan] 配置你的发送参数\n"
        "2. 使用 Chrome 扩展导出 LinkedIn cookies 到 [cyan]cookies.json[/cyan]\n"
        "3. 定制 [cyan]message/[/cyan] 目录下的消息模板\n"
        "4. 在 [cyan]urls/demo.txt[/cyan] 中添加目标联系人\n\n"
        "运行 [bold]linkedincat send --help[/bold] 查看发送命令",
        title="LinkedIn Cat Setup Guide",
        border_style="green"
    ))


@app.command()
def send(
    cookies: Path = typer.Argument(
        ..., 
        help="LinkedIn cookies JSON 文件",
        exists=True, readable=True
    ),
    message: Path = typer.Argument(
        ..., 
        help="消息模板文件",
        exists=True, readable=True
    ),
    urls: Path = typer.Argument(
        ..., 
        help="URL 列表文件",
        exists=True, readable=True
    ),
    button_class: Optional[str] = typer.Option(
        None, "--button-class", "-b",
        help="Connect 按钮的 CSS class（可选）"
    ),
    headless: bool = typer.Option(
        False, "--headless", 
        help="无头模式（不显示浏览器窗口）"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n",
        help="模拟运行，不实际发送"
    ),
    max_contacts: int = typer.Option(
        100, "--max", "-m",
        help="最大处理数量"
    ),
    force: bool = typer.Option(
        False, "--force",
        help="忽略冷却期强制发送（慎用）"
    )
):
    """
    📤 批量发送 LinkedIn 消息/好友申请
    
    [bold green]特性：[/bold green]
    
    • 智能去重：自动跳过冷却期内的联系人
    
    • 断点续传：异常中断后可恢复
    
    • 自动重试：指数退避 + 随机抖动
    
    • 安全限制：检测 LinkedIn 风控自动停止
    """
    config = LinkedinCatConfig.from_yaml()
    cache = ContactCache(config.cache_dir, config.safety.cooldown_days)
    
    msg_content = message.read_text(encoding='utf-8')
    url_lines = urls.read_text(encoding='utf-8').splitlines()
    url_list = [
        line.strip() for line in url_lines
        if line.strip() and not line.startswith('#')
    ][:max_contacts]
    
    # 显示任务预览
    preview = Table.grid(padding=1)
    preview.add_column(style="cyan", justify="right")
    preview.add_column(style="white")
    preview.add_row("消息模板:", message.name)
    preview.add_row("消息长度:", f"{len(msg_content)} 字符")
    preview.add_row("目标人数:", str(len(url_list)))
    preview.add_row("运行模式:", "[yellow]模拟运行[/yellow]" if dry_run else "[green]实际发送[/green]")
    preview.add_row("浏览器:", "[dim]无头模式[/dim]" if headless else "[blue]可见窗口[/blue]")
    
    console.print(Panel(preview, title="📋 任务预览", border_style="blue"))
    
    if not dry_run and not force:
        if not Confirm.ask("\n确认开始发送?", default=False):
            raise typer.Exit()
    
    stats = {"success": 0, "skipped": 0, "failed": 0, "cooldown": 0}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task("[green]处理中...", total=len(url_list))
        
        if dry_run:
            # 模拟运行
            for idx, url in enumerate(url_list):
                status = cache.check(url)
                if not status["can_send"] and not force:
                    if status["status"] == "cooldown":
                        days = status["cooldown_remaining"] / 86400
                        console.print(f"[yellow]⏸[/yellow] [{idx+1}/{len(url_list)}] 冷却中 ({days:.1f}天): {url[:50]}...")
                        stats["cooldown"] += 1
                    else:
                        console.print(f"[dim]⊘[/dim] [{idx+1}/{len(url_list)}] 已阻止: {url[:50]}...")
                        stats["skipped"] += 1
                else:
                    console.print(f"[blue]☐[/blue] [{idx+1}/{len(url_list)}] 模拟: {url[:50]}...")
                    stats["success"] += 1
                progress.advance(task)
                time.sleep(0.1)
        else:
            # 实际发送
            with LinkedInClient(
                cookies_path=str(cookies),
                headless=headless,
                button_class=button_class,
                max_retries=config.retry.max_retries,
                retry_delays=tuple(config.retry.delays)
            ) as client:
                
                for idx, url in enumerate(url_list):
                    # 检查缓存状态
                    status = cache.check(url)
                    
                    if not force and not status["can_send"]:
                        if status["status"] == "cooldown":
                            days = status["cooldown_remaining"] / 86400
                            console.print(f"[yellow]⏸[/yellow] [{idx+1}/{len(url_list)}] 冷却中 ({days:.1f}天): {url[:50]}...")
                            stats["cooldown"] += 1
                        else:
                            console.print(f"[dim]⊘[/dim] [{idx+1}/{len(url_list)}] 已阻止: {url[:50]}...")
                            stats["skipped"] += 1
                        
                        progress.advance(task)
                        continue
                    
                    progress.update(task, description=f"[cyan]发送给 {url[:30]}...[/cyan]")
                    
                    def on_retry(attempt):
                        progress.update(task, description=f"[yellow]重试 #{attempt}...[/yellow]")
                    
                    # 模板变量替换
                    variables = config.template_variables.copy()
                    variables["url"] = url
                    final_msg = replace_template_variables(msg_content, variables)
                    
                    result = client.send(url, final_msg, on_retry=on_retry)
                    
                    if result.status == "success":
                        cache.mark_sent(url, True, {"raw_result": result.raw_result})
                        console.print(f"[green]✓[/green] [{idx+1}/{len(url_list)}] 成功: {url[:50]}...")
                        stats["success"] += 1
                        
                    elif result.status == "blocked":
                        cache.block(url, "LinkedIn limit detected")
                        console.print(f"[red]🚫[/red] [{idx+1}/{len(url_list)}] 被 LinkedIn 阻止: {url[:50]}...")
                        console.print(Panel(
                            f"[bold red]LinkedIn 风控限制触发！[/bold red]\n"
                            f"建议：等待 24 小时后重试，或减少每日发送量",
                            border_style="red"
                        ))
                        stats["failed"] += 1
                        break  # 立即停止
                        
                    else:
                        console.print(f"[red]✗[/red] [{idx+1}/{len(url_list)}] 失败 ({result.attempts}次尝试): {url[:50]}...")
                        if result.error:
                            console.print(f"    [dim]{result.error[:100]}...[/dim]")
                        stats["failed"] += 1
                    
                    # 随机延迟
                    if idx < len(url_list) - 1:
                        delay = random.uniform(config.delay.min_seconds, config.delay.max_seconds)
                        progress.update(task, description=f"[dim]等待 {delay:.1f}s...[/dim]")
                        time.sleep(delay)
                    
                    progress.advance(task)
    
    # 最终报告
    console.print("\n")
    result_table = Table(title="📊 发送报告", show_header=True, header_style="bold")
    result_table.add_column("状态", style="dim")
    result_table.add_column("数量", justify="right")
    result_table.add_column("占比", justify="right")
    
    total = len(url_list)
    for label, count, color in [
        ("✓ 成功", stats["success"], "green"),
        ("⏸ 冷却中", stats["cooldown"], "yellow"),
        ("⊘ 跳过/阻止", stats["skipped"], "dim"),
        ("✗ 失败", stats["failed"], "red")
    ]:
        pct = f"{count/total*100:.1f}%" if total > 0 else "0%"
        result_table.add_row(f"[{color}]{label}[/{color}]", str(count), pct)
    
    console.print(result_table)
    
    # 保存运行日志
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(f"logs/run_{timestamp}.json")
    log_file.write_text(json.dumps({
        "timestamp": timestamp,
        "config": config.model_dump(),
        "stats": stats,
        "files": {
            "cookies": str(cookies),
            "message": str(message),
            "urls": str(urls)
        }
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"\n[dim]日志已保存: {log_file}[/dim]")


@app.command()
def status(
    urls: Optional[Path] = typer.Option(None, "--urls", "-u", help="检查特定 URL 列表状态")
):
    """
    📈 查看缓存状态和统计
    
    显示当前跟踪的联系人数量、冷却状态等信息。
    """
    config = LinkedinCatConfig.from_yaml()
    cache = ContactCache(config.cache_dir, config.safety.cooldown_days)
    
    stats = cache.get_stats()
    
    # 总体统计
    console.print(Panel.fit(
        f"[bold]缓存统计[/bold]\n"
        f"跟踪联系人: [cyan]{stats['total_contacts']}[/cyan]\n"
        f"冷却期中: [yellow]{stats['in_cooldown']}[/yellow]\n"
        f"可发送: [green]{stats['available']}[/green]\n"
        f"永久阻止: [red]{stats['blocked']}[/red]\n"
        f"缓存大小: [dim]{stats['cache_size_mb']:.2f} MB[/dim]",
        title="🐱 LinkedIn Cat Status",
        border_style="blue"
    ))
    
    # 如果指定了 URL 列表，显示详细状态
    if urls and urls.exists():
        url_list = [
            line.strip() for line in urls.read_text(encoding='utf-8').splitlines()
            if line.strip() and not line.startswith('#')
        ]
        
        table = Table(title=f"URL 状态检查 ({len(url_list)} 个)")
        table.add_column("URL", max_width=50, no_wrap=True)
        table.add_column("状态", justify="center")
        table.add_column("剩余冷却", justify="right")
        
        for url in url_list:
            st = cache.check(url)
            status_color = {
                "new": "green",
                "available": "blue",
                "cooldown": "yellow",
                "blocked": "red"
            }.get(st["status"], "white")
            
            remaining = ""
            if st["cooldown_remaining"]:
                days = st["cooldown_remaining"] / 86400
                remaining = f"{days:.1f}天"
            
            table.add_row(
                url[:48] + "..." if len(url) > 50 else url,
                f"[{status_color}]{st['status']}[/{status_color}]",
                remaining
            )
        
        console.print(table)


@app.command()
def reset(
    target: str = typer.Argument(..., help="重置目标: 'all', 'cooldown', 或特定 URL"),
    force: bool = typer.Option(False, "--force", help="确认重置")
):
    """
    ⚠️ 重置缓存数据（危险操作）
    
    [yellow]示例：[/yellow]
    
    • linkedincat reset all --force  # 清空所有缓存
    
    • linkedincat reset cooldown --force  # 重置所有冷却期
    
    • linkedincat reset "linkedin.com/in/xxx" --force  # 重置特定联系人
    """
    if not force:
        console.print("[yellow]⚠️ 警告：此操作不可恢复！请使用 --force 确认[/yellow]")
        raise typer.Exit(1)
    
    config = LinkedinCatConfig.from_yaml()
    cache = ContactCache(config.cache_dir, config.safety.cooldown_days)
    
    if target == "all":
        cache.reset_all()
        console.print("[green]✓ 已重置所有缓存[/green]")
    elif target == "cooldown":
        # 只重置冷却期内的记录
        count = 0
        for url in cache.get_all_urls():
            st = cache.check(url)
            if st["status"] == "cooldown":
                cache.reset(url)
                count += 1
        console.print(f"[green]✓ 已重置 {count} 个冷却期记录[/green]")
    else:
        # 重置特定 URL
        cache.reset(target)
        console.print(f"[green]✓ 已重置: {target}[/green]")


@app.command()
def export(
    output: Path = typer.Option("history.json", "--output", "-o", help="输出文件路径")
):
    """
    📦 导出缓存历史记录
    
    将所有联系人状态导出为 JSON 文件，便于备份或分析。
    """
    config = LinkedinCatConfig.from_yaml()
    cache = ContactCache(config.cache_dir, config.safety.cooldown_days)
    
    cache.export_history(str(output))
    console.print(f"[green]✓ 历史记录已导出到: {output}[/green]")


@app.command()
def version():
    """
    ℹ️ 显示版本信息
    """
    from linkedin_cat import __version__
    console.print(Panel.fit(
        f"[bold cyan]LinkedIn Cat[/bold cyan]\n"
        f"版本: [green]{__version__}[/green]\n"
        f"GitHub: https://github.com/your-repo/linkedin-cat",
        title="🐱 About",
        border_style="cyan"
    ))


def run():
    """CLI 入口点"""
    app()


if __name__ == "__main__":
    run()
