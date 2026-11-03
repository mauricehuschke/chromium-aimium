# Aimium

Aimium is a Chromium-based desktop browser project for Windows, Linux and macOS.
It is being developed around persistent website workspaces, user-selected AI
connectors and reusable visual browser workflows.

The current milestone is a **development foundation, not a production browser**.
The native `chrome://aimium` entry point is feature-gated; AI connectors, website
actions, the left sidebar and workflow execution are not implemented yet.

Start with the [Aimium project guide](aimium/README.md),
[architecture](aimium/docs/architecture.md) and
[development instructions](aimium/docs/development.md).

## Upstream Chromium

![Chromium logo](chrome/app/theme/chromium/product_logo_64.png)

Chromium is an open-source browser project that aims to build a safer, faster,
and more stable way for all users to experience the web.

The project's web site is https://www.chromium.org.

To check out the source code locally, don't use `git clone`! Instead,
follow [the instructions on how to get the code](docs/get_the_code.md).

Documentation in the source is rooted in [docs/README.md](docs/README.md).

Learn how to [Get Around the Chromium Source Code Directory
Structure](https://www.chromium.org/developers/how-tos/getting-around-the-chrome-source-code).

For historical reasons, there are some small top level directories. Now the
guidance is that new top level directories are for product (e.g. Chrome,
Android WebView, Ash). Even if these products have multiple executables, the
code should be in subdirectories of the product.

If you found a bug, please file it at https://crbug.com/new.
