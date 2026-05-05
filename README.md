# fetching the files

```bash
 uv run sync-classroom --coursework-id "862611298746"
```

# evaluating the files

```bash
uv run grade-submissions --coursework-id "862611298746" --model "gemini-2.5-flash-lite"
```

# saving and viewing the results

```bash
 uv run view-grades --coursework-id "862611298746"
```