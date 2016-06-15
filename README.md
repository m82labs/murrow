# Murrow RSS Feed Aggregator #
A simple python3 and curses-based RSS feed aggregator. This is an educational project, more advanced features will be added as I learn more.

###Current Features (however mundane they may be!):###
- 100% Keyboard navigation
- SQLite backend
- Main feed listing with unread counts
- "Send to Pocket" integration
- "Read Time" estimates for every article, based on your actual reading speed

###Planned features:###
- Full-text search
- Smart sorting
- "Time-line" style view
- Notifications
- Custom tags
- Notes
- PushBullet integration

###ISSUES###
- Some FeedBurner feeds do not properly download

###TODO###
- Write a small web service to handle pocket/etc integration authorization requests (currently using third party)
- Re-work "Read Time" estimates using on a per feed basis to account for the differences in reading speeds for different types of content
- Auto-backup config file into the database for extra portability
- Clean up the keyboard shortcuts for better UI continuity

## Installation ##
Installation is simple, just clone this repo and run `sudo make install`
