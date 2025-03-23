# api

Stores and makes available API docs for all libhal packages and their various
versions.

## 📂 File Layout

```plaintext
.
├── LICENSE
├── README.md
├── libhal
│   ├── 4.10.0
│   ├── main
│   └── switcher.json
├── <package>
│   ├── <version 1>
│   ├── <version 2>
│   └── switcher.json
└── libhal-util
    ├── 5.4.3
    ├── main
    └── switcher.json
```

Each directory corresponds to package or repo in the organization. The
subdirectories are named for each version (or branch) that API docs are made
for. Contained within are the static HTML, JS, and CSS files generated from
Doxygen and Sphinx. The `switcher.json` file is used to provide a mapping from
"version" to a URL which will appear on a drop down in the rendered
documentation. The URL for the switcher MUST be absolute and is hard coded at
documentation build time.

## 🚀 Adding API doc support for a package

### ⚙️ Deploy API Action

> [!NOTE]
> This is for libhal project only. At some later time I will document how
> general C++ projects can use this same setup to deploy API docs for
> themselves.

Add the following file to your github workflow `/.github/workflow/api.yml`:

```yaml
name: 📚 Deploy APIs

on:
  release:
    types:
      - published
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy_api_docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.x
      - run: sudo apt update
      - run: sudo apt install -y doxygen
      - run: pip install -r docs/requirements.txt gitpython requests
      - run: wget https://raw.githubusercontent.com/libhal/ci/5.x.y/scripts/api.py
      - run: python api.py build --version ${{ github.ref_name }}
      - run: python api.py deploy --version ${{ github.ref_name }} --repo-name ${{ github.event.repository.name }}
        env:
          GITHUB_TOKEN: ${{ secrets.API_PUSH_TOKEN }}
```

> [!info]
> Notice the `api.py` file. This file is the program that makes all of the
> magic happen. The script above downloads the latest `5.x.y` version of the
> script from the `libhal/ci` directory in order to build and deploy the API
> docs. If there is something wrong, its likely to have to do with the `api.py`
> script.

### 🔑 Generating PAT token

Notice the line `GITHUB_TOKEN: ${{ secrets.API_PUSH_TOKEN }}`. This is a PAT
(Personal API Token). The default `GITHUB_TOKEN` only provides limited access
to other repos. You cannot push to repos within an organization without a token
with higher permissions. You need a token that has the permissions to update
this repo and we'd like to limit that token to only being capable of updating
this repo.

1. To generate a PAT token follow the instructions in this page:
[🔗 Creating a fine-grained personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).
1. When you get to the point where you can choose the **Repository access**
   Select: `Only select repositories`.
   1. In the dropdown select: Select `<organization>/api`
1. Set **Repository Permissions** access to:
   1. Set `Contents` ➡️ Access: "Read and Write"
   1. Set `Pull Requests` ➡️ Access: "Read and Write"
1. Press **Save**
1. You should be presented with a token, copy the token value and paste to a
   text editor for safe keeping.
1. Go to your organization's secrets page using the URL:
   `https://github.com/organizations/<organization>/settings/secrets/actions`.
1. Click the button `new organization secret`
1. Set the name to `API_PUSH_TOKEN` and the value to the token you copied
   earlier. If you have no further use for the token, you can delete from your
   text editor.

### 📑 Copy `docs/` from `libhal`

The contents of `libhal`'s `docs/` directory has all of the doxygen and sphinx
files needed to generate the API docs like `libhal`. Our docs use doxygen to
generate XML docs based on the C++ code in the `include/` (the public API)
directory. This is fed into `Sphinx` using the `Breathe` plugin to combine
`doxygen` with `Sphinx`. The theme we use is the
[`PyData` theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/).

Within the `docs/libhal` directory you will find `.md` files and a `index.rst`
file. The `index.rst` file organizes all of the markdown files and the markdown
files are used to manually type out how you want the docs for a particular class
or source file to be rendered. Change these to fit your package.

Update the `json_url` for the switcher to the following and update the
`<organization>` and `<package>` templates to the correct value:

```python
html_theme_options = {
    "switcher": {
        "json_url": "https://<organization>.github.io/<organization>/<package>/switcher.json",
    },
}
```

Update these lines and replace `<package>` with the name of your package:

```python
breathe_projects = {"<package>": "../build/xml"}
breathe_default_project = "<package>"
breathe_default_members = ('members',)
project = "<package>"
```

Update `docs/index.rst` to fit what you'd like to show as the front page of your
package.

### 🎉 Done

And you are done! The next time you push to main, make a release, OR manually
run the `api.yml` workflow, your API docs will be generated, a new branch,
commit, and PR will be made to `organization/api` that you can later decide to
pull into the repo or decline.
