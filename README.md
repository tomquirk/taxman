# TAXMAN
### A CSS-based auditor that is actually useful (In Development)

![](taxman.png)

## Usage

```
from taxman import audit

...

my_audit = audit.Audit(BASE_DIR) # BASE_DIR is your website's *local* base directory
my_audit.run()
```
Have fun!

## Issues
- doesn't parse *.js* files i.e. $.addClass('myclass') won't get found

## License
MIT

## Author
Tom Quirk