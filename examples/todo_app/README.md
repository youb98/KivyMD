# KivyMD To-Do

A small but complete Material Design To-Do application built with KivyMD.

![Material Design](https://img.shields.io/badge/Material%20Design-KivyMD-teal)

## Features

- Add, complete and delete tasks.
- Tasks are persisted to `tasks.json` between runs.
- Light / dark theme toggle from the top app bar.
- Empty-state hint when there are no tasks.
- A live counter of the remaining (active) tasks in the app bar title.

## Run

```bash
python examples/todo_app/main.py
```

## Files

- `main.py` — the whole application (Python + inline KV).
- `tasks.json` — auto-created at runtime to store your tasks (git-ignored).
