
# PDF Merger Application Architecture

## Overview
The application will be built using Python and `customtkinter` for the user interface. For PDF manipulation, we will use a library like `pypdf`. The architecture will follow a clear separation of concerns, roughly adhering to the Model-View-Controller (MVC) pattern to ensure the code is maintainable and scalable.

## Architectural Components

### 1. Model (Core Logic)
Handles data and business logic, independent of the UI. This section now employs the **Strategy Pattern** to allow for interchangeable merging algorithms.

*   **`PDFManager`**: A class responsible for managing the list of files to be merged. It no longer contains the merging logic itself but delegates the merge operation to a `MergeStrategy` object.
*   **`MergeStrategy` (Abstract Base Class)**: An interface defined in `app/core/merge_strategies.py` that declares a `merge` method. All concrete merging algorithms must implement this interface.
*   **Concrete Strategies (Stateful)**:
    *   **`PyPDFMergeStrategy`**: Implements the merge logic using `pypdf`. Includes settings for PDF password protection, metadata (Title/Author), and lossless compression.
    *   **`GhostscriptMergeStrategy`**: Implements the merge logic by calling the `gs` tool. Includes settings for PDF quality profiles (`-dPDFSETTINGS`), compatibility levels, and color conversion. Features robust OS-level error handling (e.g., WSL binary detection).
*   **`Debug` System**: A singleton logger and `@debug_trace` decorator (`app/core/debug.py`) that captures function inputs/outputs and exceptions across the application.

### 2. View (User Interface)
Built with `customtkinter`. It only handles displaying data and capturing user input.
*   **`MainWindow`**: The main application window containing all frames and controls.
*   **`ExplorerFrame`**: A frame displaying available PDF files (either from a selected directory or via individual file selection).
*   **`WorkspaceFrame`**: A frame showing the list of files currently queued for merging. It will allow basic reordering or removal.
*   **`Settings Windows`**: Modal dialogs (`CTkToplevel`) specific to each merging algorithm that allow users to configure strategy parameters.
*   **`StyleManager`**: Handles dynamic theme switching (Light, Dark, System, and a custom "Tonton" theme) and persists preferences in `config.json`.
*   **Controls**:
    *   `UI Theme` dropdown to change application appearance.
    *   `Merge Algorithm` dropdown (OptionMenu) to select the desired merge strategy (e.g., PyPDF, Ghostscript).
    *   `Settings` button to open the algorithm-specific configuration window.
    *   `Select Files` button.
    *   `Merge` button.
    *   `🐞 Debug` button to open the terminal-style debug console.
    *   `StatusLabel` to display success/error messages and output paths.

### 3. Controller
Acts as the glue between the Model and View. In a simpler app, this logic often resides within the main application class.
*   Handles events like button clicks.
*   Updates the `WorkspaceFrame` when files are added or removed.
*   Instantiates the selected `MergeStrategy` based on user input from the UI.
*   Triggers the `PDFManager` to perform the merge via a background worker thread (`threading.Thread`) to prevent the UI from freezing.

## Proposed Directory Structure

```text
pdf_merger/
├── main.py                 # Entry point
├── requirements.txt        # Project dependencies
├── config.json             # Saved UI preferences
├── app/
│   ├── core/
│   │   ├── pdf_manager.py      # Manages file list and orchestrates merging
│   │   ├── merge_strategies.py # Defines the Strategy interface and concrete merge algorithms
│   │   └── debug.py            # Singleton debug console and tracing decorator
│   └── ui/
│       ├── main_window.py      # Assembles the UI and acts as Controller
│       ├── frames.py           # Explorer and Workspace frame definitions
│       ├── settings_windows.py # Algorithm-specific settings dialogs
│       └── style_manager.py    # UI theming and persistence
└── tst/                        # Testing Suite
    ├── test_pdf_manager.py
    ├── test_merge_strategies.py
    ├── test_style_manager.py
    └── test_integration.py     # End-to-end OS and file integration tests
```

## Workflows
*   **Selecting Files**: User clicks "Select Files" -> File dialog opens -> Selected files are passed to `PDFManager` -> `WorkspaceFrame` updates to show the list.
*   **Merging**: User selects a merge algorithm from the dropdown -> User clicks "Merge" -> Controller creates the corresponding `MergeStrategy` object -> Controller calls `PDFManager.merge()`, passing the strategy -> On success, `StatusLabel` updates with success message and output path; on failure, displays an error message.
