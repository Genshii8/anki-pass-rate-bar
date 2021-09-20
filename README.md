# anki-review-pass-rate-bar

This Anki addon displays a bar on the main window/deck browser that shows the pass rate of review cards over the last 7 days.

![review-pass-rate-bar](https://user-images.githubusercontent.com/1844269/132937012-b0829bf3-9a4f-4612-acbc-076dc4b80948.png)

## Configuration

### `bar.background` / `bar.foreground`

- Controls the colors of the bar.

### `passrate.time_range`

- Controls how far the addon looks back to calculate the pass rate. Default value of 7 means calculate the pass rate over the last 7 days.

## Credits

This addon is based on fonol's [anki-retention-bar](https://github.com/fonol/anki-retention-bar). All credit goes to fonol for the original source code.

I've made the following changes to the addon:

- Fixed how the bar is added to the main window/deck browser so it doesn't conflict/break other addons such as [review-heatmap](https://github.com/glutanimate/review-heatmap).
- Cleaned up/fixed the HTML/CSS for the bar.
- Removed the option to show the secondary bar that shows pass rate over the last year.
