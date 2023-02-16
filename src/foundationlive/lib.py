import datetime
import pathlib

import durations
import humanfriendly
import humanize
import jinja2
import pkg_resources

from . import model

package = __name__.split(".")[0]
templates_dir = pathlib.Path(pkg_resources.resource_filename(package, "templates"))
loader = jinja2.FileSystemLoader(searchpath=templates_dir)
env = jinja2.Environment(loader=loader, keep_trailing_newline=True)


def view1(timesheet: model.Timesheet):
    names = {}
    for entry in timesheet.days:
        for task in entry.tasks.__root__:
            names.setdefault(task.task, 0)
            duration = durations.Duration(task.task_time)
            names[task.task] += duration.to_seconds()

    by_value = sorted(names.items(), key=lambda kv: kv[1])

    stuff = []
    for task, seconds in by_value:
        delta = datetime.timedelta(seconds=seconds)
        age = humanize.naturaldelta(delta)
        stuff.append({"duration": age, "name": task})

    template = env.get_template("view1.j2")
    out = template.render(data=stuff)
    return out


def view_hours_worked_per_day(timesheet: model.Timesheet):
    stuff = []
    for entry in timesheet.days:
        seconds = 0
        tasks = []
        for task in entry.tasks.__root__:
            duration = durations.Duration(task.task_time)
            seconds += duration.to_seconds()
            tasks.append(task)

        delta = datetime.timedelta(seconds=seconds)

        x1 = {
            "date": entry.date,
            "worked_time": humanfriendly.format_timespan(delta),
            "tasks": tasks,
        }
        stuff.append(x1)

    template = env.get_template("view_hours_worked_per_day.j2")
    lst2 = sorted(stuff, key=lambda i: i["date"], reverse=True)
    out = template.render(data=lst2)
    return out


def view_hours_worked_per_day_summary(timesheet: model.Timesheet):
    daily_entries = []

    total_seconds = 0
    for entry in timesheet.days:
        seconds = 0
        for task in entry.tasks.__root__:
            duration = durations.Duration(task.task_time)
            seconds += duration.to_seconds()

        total_seconds += seconds
        delta = datetime.timedelta(seconds=seconds)

        x1 = {
            "date": entry.date,
            "worked_time": delta,
            "invoice_number": entry.invoice,
        }
        daily_entries.append(x1)

    template = env.get_template("view_hours_worked_per_day_summary.j2")
    daily_entries = sorted(daily_entries, key=lambda i: i["date"], reverse=True)
    out = template.render(
        data={
            "summary": {"total_seconds_worked": total_seconds},
            "entries": daily_entries,
        }
    )
    return out