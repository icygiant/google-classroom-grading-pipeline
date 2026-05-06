# Prerequisites:

To run the packages in this project you need to install `uv`.

* **windows**:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
* **macos/linux**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
to check the installation, run `uv --version`.

## optional - installing python using `uv`:

```uv python install``` - installs the latest versions.

```uv python install 3.11 3.12``` - one could also pin specific versions.

## making sure uv is executable 'globally' (if `uv --version` doesn't run):

* **windows**:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\.local\bin", "User")
```

* **macos/linux**:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

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