# wget https://github.com/ericchiang/pup/releases/download/v0.4.0/pup_v0.4.0_linux_amd64.zip
# unzip pup_v0.4.0_linux_amd64.zip
# chmod +x pup
# mv pup /usr/local/bin


# go to https://boardgamearena.com/gamestats?player=94506090&opponent_id=0&finished=1# and save the html as %.games.history.html

HTML_FILE = all.games.history.html
JSON_FILE = all.games.history.json

$(JSON_FILE): $(HTML_FILE)
	@cat $< | pup 'div.pagesection json{}' > $@.tmp
	@mv $@.tmp $@

all: $(JSON_FILE)
