"""
Main CLI for OTTO_Magic.
"""
import click
from core.workflows.main_workflow import video_creation_workflow

@click.group()
def cli():
    """A CLI for managing and running the OTTO_Magic video creation workflow."""
    pass

@click.command()
@click.option('--topic', default='AI in 2025', help='The topic for the video.')
@click.option('--custom-brief', default=None, help='A custom brief for the video.')
def run_workflow(topic: str, custom_brief: str | None):
    """Manually trigger the video creation workflow."""
    try:
        video_creation_workflow(topic, custom_brief)
        print("Workflow execution completed.")
    except Exception as e:
        print(f"Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()

@click.command()
def deploy():
    """Deploy the video creation workflow with a schedule."""
    print("Deployment functionality requires additional setup. Use 'prefect deploy' command instead.")

cli.add_command(run_workflow)
cli.add_command(deploy)

if __name__ == '__main__':
    cli()
