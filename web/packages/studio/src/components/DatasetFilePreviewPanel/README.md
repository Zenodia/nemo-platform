# DatasetFilePreviewPanel

Dataset file preview side panel with automatic content rendering, data fetching, and breadcrumb navigation.

## Features

- **Automatic breadcrumb generation** from dataset name and file path
- Automatic data fetching (with optional pre-fetched data support)
- JSON rendering with CodeEditor
- **Preformatted text fallback for non-JSON files**
- Loading and error states
- All file actions (download, rename, delete, split)
- Router-agnostic (all navigation via callbacks)

## Usage

### Basic Example (Internal Data Fetching)

```typescript
import { DatasetFilePreviewPanel } from '@studio/components/DatasetFilePreviewPanel';

const MyComponent = () => {
  return (
    <DatasetFilePreviewPanel
      open={true}
      datasetNamespace="default"
      datasetName="my-dataset"
      filePath="data/train.txt"
      onDatasetClick={() => navigate('/filesets/my-dataset')}
      onFolderClick={(folderPath) => navigate(`/filesets/my-dataset/files/${folderPath}`)}
      onCloseClick={() => navigateToPreviousView()}
      onOutsideClick={() => navigateToList()} // Optional: different behavior for outside clicks
      onDeleteSuccess={() => handleFileDeleted()}
      onRenameSuccess={(newPath) => navigateToFile(newPath)}
      // Component fetches data and generates breadcrumbs automatically!
      // Breadcrumbs: "my-dataset" > "data" > "train.txt"
      // Both dataset and folder breadcrumbs are clickable!
    />
  );
};
```

### With Pre-Fetched Data

```typescript
const { data: fileContent, isLoading, error } = useDatasetFileContent({
  namespace: 'default',
  name: 'my-dataset',
  path: 'data.txt',
});

return (
  <DatasetFilePreviewPanel
    open={true}
    datasetNamespace="default"
    datasetName="my-dataset"
    filePath="data.txt"
    fileContent={fileContent}
    isLoading={isLoading}
    error={error}
    onCloseClick={() => navigateToPreviousView()}
    onOutsideClick={() => navigateToList()}
  />
);
```

## File Type Handling

The component automatically detects file type and renders appropriately:

- **JSON files** (`.json`, `.jsonl`): Rendered with CodeEditor
- **Text files** (`.txt`, `.log`, `.csv`, etc.): Rendered with preformatted text
- **All other files**: Rendered with preformatted text fallback

### Preformatted Text Fallback

For non-JSON files, content is rendered in a `<pre>` tag with:

- Preserved whitespace
- Monospace font
- Word wrapping (`whitespace-pre-wrap`)
- Scrollable container

## Props

| Prop               | Type                           | Required | Description                                                                                                             |
| ------------------ | ------------------------------ | -------- | ----------------------------------------------------------------------------------------------------------------------- |
| `open`             | `boolean`                      | Yes      | Whether the panel is open                                                                                               |
| `onOpenChange`     | `(open: boolean) => void`      | No       | Called when panel open state changes. If provided, prevents onCloseClick from being called to avoid duplicate handling. |
| `onCloseClick`     | `() => void`                   | Yes      | Called when close button clicked (or when closing via other means if onOpenChange not provided)                         |
| `onOutsideClick`   | `() => void`                   | No       | Called when clicking outside or pressing ESC. If not provided, falls back to onCloseClick.                              |
| `datasetNamespace` | `string`                       | Yes      | Dataset namespace                                                                                                       |
| `datasetName`      | `string`                       | Yes      | Dataset name (used in breadcrumbs)                                                                                      |
| `filePath`         | `string`                       | Yes      | Path to file in dataset (used in breadcrumbs)                                                                           |
| `onDatasetClick`   | `() => void`                   | No       | Called when dataset breadcrumb is clicked                                                                               |
| `onFolderClick`    | `(folderPath: string) => void` | No       | Called when folder breadcrumb is clicked with the folder path                                                           |
| `onDeleteSuccess`  | `() => void`                   | No       | Called after successful file deletion                                                                                   |
| `onRenameSuccess`  | `(newPath: string) => void`    | No       | Called after successful file rename                                                                                     |
| `file`             | `FileSystemFile`               | No       | Pre-fetched file metadata                                                                                               |
| `fileContent`      | `string`                       | No       | Pre-fetched file content                                                                                                |
| `isLoading`        | `boolean`                      | No       | Loading state (if pre-fetched)                                                                                          |
| `error`            | `Error`                        | No       | Error state (if pre-fetched)                                                                                            |

## Breadcrumb Generation & Navigation

Breadcrumbs are automatically generated from `datasetName` and `filePath`:

```typescript
// Given:
datasetName = 'my-dataset';
filePath = 'data/subfolder/train.jsonl';

// Generates breadcrumbs:
// "my-dataset" > "data" > "subfolder" > "train.jsonl"
```

### Breadcrumb Behavior:

- **Dataset breadcrumb** (first): Clickable if `onDatasetClick` provided
- **Folder breadcrumbs** (middle): Clickable if `onFolderClick` provided
  - Clicking passes the full path to that folder (e.g., `"data"`, `"data/subfolder"`)
- **File breadcrumb** (last): Always non-clickable (current file)

### Navigation Example:

```typescript
<DatasetFilePreviewPanel
  datasetName="my-dataset"
  filePath="data/subfolder/train.jsonl"
  onDatasetClick={() => {
    // Navigate to dataset root
    navigate('/filesets/my-dataset');
  }}
  onFolderClick={(folderPath) => {
    // Navigate to folder view
    // folderPath will be: "data" or "data/subfolder"
    navigate(`/filesets/my-dataset/files/${folderPath}`);
  }}
/>
```

## When to Use

Use DatasetFilePreviewPanel when you need a file preview panel for dataset files with:

- Automatic breadcrumb navigation
- Automatic content rendering (JSON or text)
- Built-in file actions
- Automatic or manual data fetching
