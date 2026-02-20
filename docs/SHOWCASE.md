# Showcase

## Real-World Usage Examples

### Finding Issues
```bash
gfi find --lang python --lang rust
```

![Search Results](https://via.placeholder.com/800x400?text=Screenshot+Coming+Soon)

### Viewing Issue Details
```bash
gfi show https://github.com/django/django/issues/18469
```

Displays:
- **Overall Score**: 0.72 (Good)
- **Clarity**: 0.80 (Clear checklist and description)
- **Maintainer Response**: 1.00 (Django is very responsive)
- **Freshness**: 0.20 (Older issue)
- **Project Activity**: 0.70 (86.9k stars, active project)

### Filtering Options

**By Language:**
```bash
gfi find --lang javascript --lang typescript --lang go
```

**By Project Size:**
```bash
gfi find --min-stars 1000  # Popular projects only
gfi find --min-stars 10    # Include smaller projects
```

**By Age:**
```bash
gfi find --max-age 7    # Last week
gfi find --max-age 30   # Last month
gfi find --max-age 180  # Last 6 months
```

**Combination:**
```bash
gfi find --lang rust --min-stars 500 --max-age 14 --limit 20
```

## Success Stories

*Have you used GFI to find your first contribution? Share your story by opening an issue!*

## Tips for Best Results

1. **Start broad**: Use `--min-stars 1` and `--max-age 180` initially
2. **Multiple languages**: Try 2-3 languages you know
3. **Trust the scores**: 0.7+ issues are usually excellent
4. **Check the details**: Use `gfi show` before committing
5. **Look for patterns**: Active projects with clear issues get high scores

## Featured Projects Using GFI

*Does your project use GFI? Let us know!*
