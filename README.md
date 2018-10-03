# podbay-dl
download all of an uploaders podcasts using uploader id's and url's.

## Setup
firstly, the `requests` and  `bs4` modules are required to run this script. do `$ pip install requests bs4` to install both of these modules.

optionally you may also install the `progress` module (also available with pip) to get a pretty progress bar view :-).

## How to use this
### Calling from the command line
use `$ podbay-dl http://podbay.fm/show/360084272`, or more easily, you may omit the 'http://podbay.fm/show/' like so `$ podbay-dl 360084272`, you may also string as many id's or url's at the end of the command and they will be downloaded sequentially. `$ podbay-dl 360084272 1113585468`

### Import
this is how to use it from within the python code itself.
```
import podbay-dl
show_id = '360084272' # The full URL works as well, just as with the cmd line method
uploader = Podbay(show_id)
uploader.download()
```
