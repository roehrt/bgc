GEN=python analyze.py --web
WEB_OUT=../website/_includes/results

all: official fixed
official: ${WEB_OUT}/official-summary.html ${WEB_OUT}/official-full.html
fixed: ${WEB_OUT}/fixed-summary.html ${WEB_OUT}/fixed-full.html
summary: ${WEB_OUT}/official-summary.html ${WEB_OUT}/fixed-summary.html
full: ${WEB_OUT}/official-full.html ${WEB_OUT}/fixed-full.html

${WEB_OUT}/official-summary.html: official/*.csv
	$(GEN) --summary --set $^ > $@

${WEB_OUT}/official-full.html: official/*.csv
	$(GEN) --set $^ > $@

${WEB_OUT}/fixed-summary.html: fixed/*.csv
	$(GEN) --summary --set $^ > $@

${WEB_OUT}/fixed-full.html: fixed/*.csv
	$(GEN) --set $^ > $@

clean:
	rm -f ${WEB_OUT}/official-summary.html ${WEB_OUT}/official-full.html
	rm -f ${WEB_OUT}/fixed-summary.html ${WEB_OUT}/fixed-full.html