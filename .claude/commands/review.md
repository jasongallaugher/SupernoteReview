---
description: Send a markdown file to Supernote device for human review
allowed-tools: Bash(sn-review:*)
argument-hint: [file path]
---

You will send a markdown file to the Supernote device for human review using the sn-review CLI.

**Before proceeding, confirm with the user that they want to send the file for review.** This operation transfers the file to their Supernote device where they will annotate it.

Once confirmed, run the command:
```bash
sn-review review $ARGUMENTS
```

After the command completes, inform the user that the file has been sent to their Supernote device for review. They can now annotate it and retrieve the changes using the `/done` command when finished.
