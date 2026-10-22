import sys
from django.core.management.base import BaseCommand, CommandError
from portfolio.tasks import update_hackerrank_badges, check_ntfy_status_updates


TASKS = {
    "hackerrank": {
        "fn": update_hackerrank_badges,
        "name": "HackerRank Badges Ingestion",
        "description": "Fetches and stores latest HackerRank badge snapshot.",
    },
    "ntfy": {
        "fn": check_ntfy_status_updates,
        "name": "NTFY Status Poller",
        "description": "Polls NTFY server for latest status message updates.",
    },
}


class Command(BaseCommand):
    help = "Run background/periodic tasks on demand (locally or enqueued via Huey)."

    def add_arguments(self, parser):
        parser.add_argument(
            "task_name",
            nargs="?",
            default=None,
            help=f"Task identifier to run ({', '.join(TASKS.keys())}, or 'all').",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List all registered runnable tasks.",
        )
        parser.add_argument(
            "--enqueue",
            action="store_true",
            help="Enqueue into Huey task queue instead of executing synchronously in the current process.",
        )

    def handle(self, *args, **options):
        if options["list"] or not options["task_name"]:
            self.stdout.write(self.style.SUCCESS("Available on-demand tasks:"))
            for key, meta in TASKS.items():
                self.stdout.write(f"  - {self.style.WARNING(key)}: {meta['name']} ({meta['description']})")
            self.stdout.write(f"  - {self.style.WARNING('all')}: Run all tasks sequentially.")
            self.stdout.write("\nUsage:")
            self.stdout.write("  python manage.py run_task <name>           # Run synchronously")
            self.stdout.write("  python manage.py run_task <name> --enqueue # Enqueue to Huey worker")
            return

        target = options["task_name"].lower()
        if target == "all":
            to_run = list(TASKS.keys())
        elif target in TASKS:
            to_run = [target]
        else:
            valid = ", ".join(list(TASKS.keys()) + ["all"])
            raise CommandError(f"Unknown task '{target}'. Choose from: {valid}")

        enqueue = options["enqueue"]

        for key in to_run:
            meta = TASKS[key]
            task_wrapper = meta["fn"]
            name = meta["name"]

            if enqueue:
                self.stdout.write(f"Enqueuing task [{key}] ({name}) into Huey queue...")
                try:
                    result = task_wrapper()
                    self.stdout.write(self.style.SUCCESS(f"✓ Enqueued [{key}] successfully (task ID: {getattr(result, 'id', 'N/A')})."))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"✗ Failed to enqueue [{key}]: {e}"))
            else:
                self.stdout.write(f"Executing task [{key}] ({name}) synchronously...")
                try:
                    result = task_wrapper.call_local()
                    self.stdout.write(self.style.SUCCESS(f"✓ Finished [{key}]. Result: {result}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"✗ Error executing [{key}]: {e}"))
