# Sensory gate — judgment cases

Three reviews that passed and should not have. Each is generalised; each ends in the rule it bought.

## 1. The preview pane invented the defect

A review round was performed against a video file as it played inside a coding tool's preview pane. The pane dropped frames and rescaled, and both showed up as stutter. Three fix cycles were spent chasing motion artifacts that existed only in the preview; the file on disk had been clean since the first render.

**Rule:** sensory review happens against the real output file, opened the way the audience will open it. A preview is a rendering of the file, not the file.

## 2. The contact sheet hid the thing it was made to catch

A batch of generated images was signed off from a single downscaled contact sheet. A malformed hand — obvious at full resolution — occupied a few pixels at thumbnail scale and shipped. The same reviewer caught it in two seconds once the region was cropped at 1:1.

A contact sheet answers *which one should I look at*. It cannot answer *is this one correct*, and the two questions feel identical while you are looking at it.

**Rule:** fine detail is signed off from a crop at 1:1 or greater of the specific region. The contact sheet stays useful for triage.

## 3. The closed gate still held its rejects

A task was reported complete while the `NG/` folder from an early round still held the files the human had rejected. Weeks later a batch job walked the whole review tree and pulled the rejected takes back into a build, because on disk they were simply files sitting in the project.

**Rule:** emptying `NG/` is part of closing out. A rejection recorded only as a file's location stops being a rejection the moment something else reads that folder.
