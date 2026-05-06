# Prerequisites:

## `uv`

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

### optional - installing python using `uv`:

```uv python install``` - installs the latest versions.

```uv python install 3.11 3.12``` - one could also pin specific versions.

### making sure uv is executable globally (if `uv --version` doesn't run):

* **windows**:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\.local\bin", "User")
```

* **macos/linux**:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

## google auth credentials.

Google Classroom requires a user-contextual identity to access specific student data, so one cannot, to the best of my knowledge, use a service account in this specific case. you'll need to use the oauth 2.0 desktop application flow, which involves a one-time browser login to generate a "refresh token," which the packages here can then use to act on your behalf. To do so, you must register your application in the [Google Cloud Console](https://console.cloud.google.com/).

1. create a new project, if you haven't already.

2. go to `Enabled APIs & Services` and enable `Google Classroom API` and `Google Drive API`.

3. configure OAuth Consent Screen - choose `internal` (if you're in a Google Workspace) or `external`.

4. add these three scopes to the "Scopes" section:
```
[
    "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
    "https://www.googleapis.com/auth/classroom.rosters.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]
```
crucial: if you chose "external" and your app is in "testing" mode, you must add your own email address as a test user.

5. go to `Credentials` -> `Create Credentials` -> `OAuth client ID`. select `Application type: Desktop App`. download the json file and rename it to credentials.json. place it in `secrets/` directory in the project root.

## gemini api auth

1. visit [google ai studio](https://aistudio.google.com/)

2. sign in with your standard Google account

3. accept the Terms of Service.

4. click `Create API key`

5. copy the key and save it immediately in a secure location (or an `.env` file in the project root)


# fetching the files

```bash
 uv run sync-classroom --coursework-id "862611298746"
```

`sync-classroom` also accepts the following options:

* `--course-id` - `'845870833845'` by default (a by-product of me sharing this with a specific user, naturally, one would always change that for their own personal use (or change the default value when forking this project))

* `--staging-dir`, the path where the downloaded files are saved

* `--manifest-path`, the path where the manifest file with the metadata on the downloaded files is saved

* `--credentials`, the path where the google auth credentials json is saved.

* `--token`, the path where the google auth session token json is saved.

* `--ext` file extensions accepted by the parser, defaults to `[".py", ".sql", ".txt", ".pdf"]`.

# evaluating the files

```bash
uv run grade-submissions --coursework-id "862611298746"
```
`grade-submissions` also accepts the following options:

* `--model`, defaults to "gemini-2.5-flash"

* `--delay`, number of seconds that the script waits between evaluating each student to dodge rpm limits, defaults to 5.

# saving and viewing the results

```bash
 uv run view-grades --coursework-id "862611298746"
```