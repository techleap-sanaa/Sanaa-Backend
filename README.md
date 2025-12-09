# Sanaa Backend

This repository holds the server side of Sanaa — a centralized, localized digital platform designed to solve the fragmentation and unfairness faced by the creative community. It provides a single hub where creatives can post all their content and build genuine community engagement. Sanaa introduces a fairer discovery model through an unbiased algorithm, allowing all creators to gain visibility organically. Crucially, it enables creatives to monetize their craft directly from their fans through dedicated support tools. By prioritizing localization, Sanaa ensures content and events are relevant to the creator’s geographic context, building stronger real-world connections.

Here is the correctly formatted Markdown:

## 💻 Technologies

1.  **Django** + **Django REST Framework (DRF)**
2.  **Clerk API**
3.  **Git/Github**

---

## 🛑 Rules for Contributors

1.  **NEVER** merge directly to the **main** branch. Instead, create a **Pull Request (PR)** to merge into **test-branch**.
2.  **Test locally** before pushing to make PR approval and merging more efficient.
3.  Always run `git pull origin test-branch` while **IN** the **test-branch** before any major local changes to ensure frequent syncing with the remote repo.

## 🔄 Typical Workflow

### ⚙️ Explaining the Git Commands

The commands in your workflow are used for coordinating changes between your local machine, the team's shared remote repository, and a specific feature you are working on.

| Command | Purpose |
| :--- | :--- |
| `git checkout test-branch` | Switches your local working environment to the `test-branch`. You typically do this to make sure you have the latest approved changes before starting new work. |
| `git pull origin test-branch` | Fetches the latest changes from the remote repository's `test-branch` (`origin`) and merges them into your local `test-branch`. This **synchronizes** your local copy. |
| `git checkout -b name/branch-name` | **Creates a new branch** (e.g., `feature/login-fix` or `bug/201`) based on the current branch (which should be `test-branch`) and immediately switches to it. This isolates your work. |
| `git add .` | Stages all modified and new files in your current working directory for the next commit. |
| `git commit -m "..."` | Records the staged changes to your local branch history with a descriptive message. |
| `git merge name/branch-name` | Integrates the history from the specified branch (`name/branch-name`) into your currently checked-out branch (which should be `test-branch`). |
| `git push origin name/branch-name` | Uploads your local branch and its commits to the remote repository on GitHub so you can create a Pull Request. |

---

### 🌟 Standardized Workflow

This simplified approach follows a **Feature Branching** strategy:

1.  **Get the Latest:**
    * `git checkout test-branch`
    * `git pull origin test-branch`
2.  **Create Your Isolated Feature Branch:**
    * `git checkout -b feature/my-new-feature`
3.  **Work and Commit:**
    * Make changes (e.g., edit files).
    * `git add .`
    * `git commit -m "feat: implemented X functionality"`
    > **💡 Pro-Tip:** Do this often! Small, frequent commits are easier to review.
4.  **Before Pushing (Optional but Recommended Sync):**
    * If the work takes a long time, bring in the latest `test-branch` changes *into* your feature branch to handle conflicts locally:
        * `git pull origin test-branch` (This automatically tries to merge/rebase the latest test-branch into your current feature branch).
        * Resolve any conflicts locally and commit the merge if necessary.
5.  **Push and Create PR:**
    * `git push origin feature/my-new-feature`
    * Go to GitHub and **Create a Pull Request (PR)** from `feature/my-new-feature` to **`test-branch`**.
    > **This PR step is how all the merging, conflict resolution, and testing should be finalized.**

---
