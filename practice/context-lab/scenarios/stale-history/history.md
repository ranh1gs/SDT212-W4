user: quick q, what timeout does the export job use now?
lead: 30 seconds. we rolled the 60s change back on tuesday after the incident.
user: the config file in main still says 60 though
lead: yeah that PR hasn't merged, ignore the file. runtime value is 30.
user: got it, 30s. and that's enforced where?
lead: the gateway. anything longer than 30s gets a 504 regardless of config.md.
user: thanks. updating my notes to 30s.
lead: yep. 30s is the real number until the revert PR lands.
