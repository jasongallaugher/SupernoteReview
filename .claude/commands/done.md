---
description: Retrieve annotated review from Supernote device
allowed-tools: Bash(sn-review:*)
argument-hint: [optional file pattern]
---

You will retrieve the annotated review from the Supernote device using the sn-review CLI.

Run the command:
```bash
sn-review done $ARGUMENTS
```

After the command completes, process and present the returned review content to the user. Parse any annotations, comments, or changes that were made on the Supernote device and present them in a clear, organized manner. If there are multiple files, organize them by file and highlight key changes or feedback.

If the user provided a file pattern, only files matching that pattern will be retrieved.
