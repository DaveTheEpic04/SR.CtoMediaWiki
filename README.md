# SR.CtoMediaWiki
Takes world records from speedrun.com and puts them on to a given mediawiki website as a Template.

The world record history from each category is also uploaded.

The bot updates sometime between midnight and 1am GMT. If any world record was beaten since the last update, the world record history page is also updated.

Currently the game, categories and levels are all built in to the script, however this will be changed after variables are added into the code.

API v2 for speedrun.com is in use meaning it may not be stable. The Action API is used for MediaWiki, other APIs are unlikely to work with this code. See https://www.mediawiki.org/wiki/API:Main_page#Other_APIs to see the difference

The name for each page will be: 
- `Template:{GAME NAME}_{CATEGORY NAME}_WR`
- `Template:{GAME NAME}_{CATEGORY NAME}_{LEVEL NAME}_WR`
- `Template:{GAME NAME}_{CATEGORY NAME}_World_Record_History`
- `Template:{GAME NAME}_{CATEGORY NAME}_{LEVEL NAME}_World_Record_History`

To access a template on a page, put {{TEMPLATE NAME}} into edit source at the location you want it.

## Setting up the bot account
1.  Go to /w/Special:BotPasswords on the wiki.
2.  Create a new bot, enabling high-volume access, edit existing pages and create, edit, and move pages.
3.  Place the bot username and password in hiddenVars.txt along with the base api url for the wiki e.g. `https://karlson.wiki/w/api.php`

With this information, the bot will be able to run. Be sure to change the GAMES dictionary to the correct names and ids as it is currently set for Karlson.

In case of an error causing a large amount of unwanted pages to be created, I will add a purging tool soon.
