# Media Export Builder Specification

## 1. Overview

Build a Python application that generates exports from a media library.

The application shall:

- Scan one or more source directories.

- Select media files that have not previously been added to an export.

- Copy those files into export directories.

- Track previously selected files using a persistent watched file.

- Produce a summary report after each execution.

The application is intentionally simple.

- No database shall be used.

- All persistent state shall be stored in files.

- Source media shall never be modified.

---

# 2. Configuration

The application shall load its configuration from a YAML configuration file.

The configuration shall contain:

- One or more source directories.

- The destination root directory.

- The number of files to place into each export.

- The path to the watched file.

- A list of supported media file extensions.

Example:

```yaml

source_directories:

  - /media/library/Action

  - /media/library/Comedy

target_root_directory: /media/exports

files_per_export: 10

watched_file_path: /media/watched.txt

supported_extensions:

  - .mp4

```

### Configuration Fields

| Field | Description |

|--------|-------------|

| `source_directories` | List of source category directories to process. |

| `target_root_directory` | Root directory where exports will be generated. |

| `files_per_export` | Number of files to generate for each category. |

| `watched_file_path` | Path to the persistent watched list. |

| `supported_extensions` | File extensions to include when scanning. Matching is case-insensitive. |

---

# 3. Source Library

## Categories

Each configured source directory represents a category.

The category name is the name of the directory itself.

Example:

```

/media/library/Action

/media/library/Comedy

```

Produces the categories:

- Action

- Comedy

---

## Directory Structure

Categories may contain subdirectories.

Subdirectories exist only for organizational purposes.

The application shall recursively scan every subdirectory and treat all supported media files as belonging to the parent category.

Example:

```

Action/

    Movie1.mp4

    Classics/

        Movie2.mp4

    New/

        Movie3.mp4

```

All three files belong to the **Action** category.

---

## Filename Uniqueness

All filenames in the media library are expected to be unique within a category, regardless of their parent directory.

For example, these are considered duplicates:

```

Action/Classics/Movie1.mp4

Action/New/Movie1.mp4

```

Duplicate filenames represent a data quality issue.

If duplicates are detected, the application shall:

- Report every duplicate filename.

- Report the full path of every duplicate.

- Continue processing by selecting one representative file for each duplicate filename.

The user is expected to resolve duplicate filenames in the source library.

---

# 4. Watched File

## Purpose

The watched file records which files have previously been added to exports.

This is the application's only persistent state.

---

## Format

The watched file is a plain text file.

Each line contains:

```

<category>/<filename>

```

Example:

```

Action/Movie1.mp4

Action/Movie2.mp4

Comedy/FunnyMovie.mp4

```

---

## Behavior

A file is considered watched if an entry matching its category and filename exists in the watched file.

---

## Reset

The application shall support resetting the watched list for an individual category.

Resetting a category removes every entry whose category matches the specified category.

Example:

```bash

python media_export_[builder.py](http://builder.py) --reset-category Action

```

The application shall also support resetting the entire watched list.

Example:

```bash

python media_export_[builder.py](http://builder.py) --reset-all-watched

```

Only the watched file is modified.

Source files and export directories are not modified.

---

# 5. Export Generation

## Destination Structure

Generated exports shall be written to:

```

target_root_directory/

    Action/

    Comedy/

```

No additional export subdirectories are created.

---

## Destination Validation

Before any processing begins, the application shall verify that the configured `target_root_directory`:

- Exists.

- Is a directory.

- Contains no files or subdirectories.

If the destination root directory fails any of these checks, the application shall:

- Display an error explaining the problem.

- Perform no further processing.

- Leave the destination unchanged.

- Leave the watched file unchanged.

Example:

```

ERROR

Target root directory is not empty:

/media/exports

Please remove the existing export before running the application.

```

---

## File Copy

Files shall be copied.

Exported files shall retain their original filename, with only the configured numeric prefix prepended.

Example:

```

Original:

Movie1.mp4

Export:

02-Movie1.mp4

```

Source files shall never be moved, renamed, or modified.

---

## Prefix Distribution

Each exported filename shall receive one of the following prefixes:

```

00

02

04

06

```

The prefixes shall be assigned using the following weighted distribution:

| Prefix | Percentage |

|--------|-----------:|

| 00 | 10% |

| 02 | 30% |

| 04 | 30% |

| 06 | 30% |

The distribution shall scale automatically based on `files_per_export`.

Example for an export containing ten files:

```

00-file.mp4

02-file.mp4

02-file.mp4

02-file.mp4

04-file.mp4

04-file.mp4

04-file.mp4

06-file.mp4

06-file.mp4

06-file.mp4

```

If rounding is required, the application shall preserve the configured ratios as closely as possible while ensuring the export contains exactly the requested number of files.

---

## Prefix Assignment

The application shall:

1. Select all export files.

2. Randomly shuffle the selected files.

3. Assign prefixes according to the configured distribution.

This ensures an unbiased distribution of prefixes.

---

# 6. Processing Pipeline

The application shall perform the following steps:

1. Load the configuration.

2. Validate the destination root directory.

3. Load the watched file.

4. For each configured category:

    1. Recursively scan the source directory.

    2. Collect files whose extensions match `supported_extensions`.

    3. Detect duplicate filenames.

    4. Select one representative file for each duplicate filename.

    5. Remove watched files.

    6. Randomly select up to `files_per_export` files.

    7. Randomly shuffle the selected files.

    8. Assign weighted prefixes.

    9. Copy the files into the destination category directory.

    10. Update the watched file.

5. Generate the final report.

If fewer unwatched files exist than requested, all remaining files shall be selected.

---

# 7. Reporting

After execution, the application shall produce a report.

For each category, the report shall include:

- Number of files added.

- Number of watched files.

- Number of unwatched files remaining.

Example:

```

Export Summary

Category: Action

Added: 10

Watched: 132

Remaining: 418

```

## Duplicate Filename Report

Duplicate filenames shall be reported separately.

Example:

```

Duplicate Filenames

Category: Action

Movie1.mp4

    /media/library/Action/Classics/Movie1.mp4

    /media/library/Action/New/Movie1.mp4

```

Duplicate filenames are informational only and do not prevent export generation.

---

# 8. Constraints

The application shall:

- Never modify source files.

- Never use a database.

- Store all persistent state in the watched file.

- Continue processing when duplicate filenames are detected.

- Produce deterministic behavior except where randomness is explicitly required.

---

# 9. Non-Goals

The application will not:

- Provide a graphical user interface.

- Stream media.

- Connect to external services.

- Read media metadata.

- Rename source files.

- Organize the media library.

---

# 10. Design Philosophy

The application intentionally separates responsibilities.

| Component | Responsibility |

|-----------|----------------|

| Source library | Permanent media storage |

| Watched file | Persistent export history |

| Media Export Builder | Selection and export |

| Export directories | Current playback content |

| Media player | Playback only |

---

# 11. Command Line Interface

## Generate Exports

Generate exports using the default configuration file.

```bash

python media_export_[builder.py](http://builder.py)

```

---

## Alternate Configuration

Generate exports using a specific configuration file.

```bash

python media_export_[builder.py](http://builder.py) --config /path/to/config.yaml

```

---

## Reset a Category

Remove all watched entries for a single category.

```bash

python media_export_[builder.py](http://builder.py) --reset-category Action

```

The reset operation modifies only the watched file.

No source files or export directories are modified.

---

## Reset All Watched

Remove every entry from the watched file.

```bash

python media_export_[builder.py](http://builder.py) --reset-all-watched

```

The reset operation modifies only the watched file.

No source files or export directories are modified.

---

## Combined Usage

The `--config` option may be combined with `--reset-category` or `--reset-all-watched`.

Example:

```bash

python media_export_[builder.py](http://builder.py) \

    --config /path/to/config.yaml \

    --reset-category Action

```

The specified configuration file determines the location of the watched file and the available categories.

---

## Exit Codes

| Exit Code | Meaning |

|-----------|---------|

| 0 | Success |

| 1 | Configuration error |

| 2 | Destination validation failed |

| 3 | Invalid command-line arguments |

| 4 | Unexpected runtime error |