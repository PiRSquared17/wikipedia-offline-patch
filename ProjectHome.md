_Supported platforms: MacOS, Windows, Linux_

This extension provides an offline viewing mode for Wikipedia backup dumps (for example, a recent [English](http://download.wikimedia.org/enwiki/20101011/enwiki-20101011-pages-articles.xml.bz2), compressed backup of all article text (6.3GB), or any [other](http://dumps.wikimedia.org/backup-index.html) language or collection).

_Note_: The officially-recommended offline reader for wikipedia is [Kiwix](http://www.kiwix.org/).

## WHY ##
Loading the full, uncompressed contents of wikipedia can require prohibitive amounts of disk space.  Running a database server can also present a technical challenge.  Other methods of providing "offline" content have the disadvantage of requiring the database to be decompressed, and converted to another format, and use a non-native presentation engine.  Reconverted databases are not yet available in most languages.

The long-term goal of this project is to allow for distributed editing by peer-to-peer nodes, each capable of storing offline content in several languages, and a live database of edits which can be batched and synchronized.  See [Distributed Revision Control](http://en.wikipedia.org/wiki/Distributed_revision_control) and [Git](http://en.wikipedia.org/wiki/Git_(software)).

## Howto ##
Read INSTALL below for the quick-starter.  Be aware that an [indexed](#YOUR_ENCYCLOPEDIA_and_its_INDEX.md) Wikipedia dump must be obtained independently in order to install this software.

The genuine MediaWiki rendering engine is still doing all the hard work, the idea is that we are just replacing the storage.  Technology requirements are the same as for MediaWiki: the PHP language plus several extensions, and a web server.  Standalone web servers and configuration files are bundled with the binary release: Hiawatha, Mongoose, and Apache.  You will be able to share your copy of the encyclopedia with others on your network.


# Acknowledgements #
The current author is Adam Wight, who can be reached through this [project page](http://code.google.com/p/wikipedia-offline-patch/) or at adamw on ludd.net.

[Thanassis Tsiodras](http://users.softlab.ece.ntua.gr/~ttsiod/buildWikipediaOffline.html) has a great page explaining how to build an offline wikipedia using the fslab patches, below.

[Wikipedia Offline Client](https://projects.fslab.de/projects/wpofflineclient/) was the starting point for this code.

This software and its source code are licensed as GPL.


---

# Installing wikipedia offline patch #
You have the choice to install the mediawiki extension, or a binary package preconfigured for standalone use.

If you are only installing the mediawiki "Offline" extension, take a look in `wikipedia-offline-patch/config/LocalSettings.php` and copy any lines you might need.  Look in the [Special:Offline](http://localhost:8000/wiki/index.php?title=Special:Offline) page for status and diagnostic hints once your system is running.

> a) Linux
    * Dependencies:
```
    yum install php xapian-core xapian-bindings php-pecl-apc
```

> b) Windows
  * The windows package comes with all dependencies locally installed, but you might still have to take these steps:
```
    copy zlib1.dll C:\windows\system32\
```
  * You need the MSVC 2008 Runtime compatibility library.
  * If you are not using the bundled mongoose webserver and php, you will need to include windows/php.ini during php startup.

> c) MacOS
    * If you are running MacOS 10.4, you will need to upgrade to php5, installing it into `/usr/local` is recommended. Install the "apc" accelerator and xapian php binding, and enable in `php.ini`.
    * Somehow install the xapian library.
    * You might need to recompile the indexer, or deal with `ld.config` and `ldd`
```
    PHP_CONFIG=/usr/local/php5/bin/php-config XAPIAN_CONFIG=/usr/local/bin/xapian-config ./configure --with-php
```
    * you also may need to edit "-Wstrict-null-sentinel" out of the configure script.


## YOUR ENCYCLOPEDIA and its INDEX ##

Install an xml dump of your wikipedia, probably distributed in a file named `pages-articles.xml.bz2`,
from a disc or the net.  Check in often with bittorrent networks.  Try to download the corresponding index files, in any of the formats (well only Xapian for the moment).  Otherwise, you will have to generate the index yourself, read on brave soul.  An index is necessary to match a given article with its location in your dumpfiles.

(You can get a small, pre-indexed encyclopedia for testing purposes
from yours truly, [wiki-splits-tl.zip](http://code.google.com/p/wikipedia-offline-patch/downloads/list) for example.)

Extract, then either create a link
```
    ln -s ~/wiki-splits-tl/ wiki-splits
```
or rename your database dump directory to `./wiki-splits`

Of course, you can always edit `mediawiki/LocalSettings.php` and set the `$wgOfflineWikiPath` variable to point to another directory.

> Hint, your files should look something like this:
```
drwxrwxr-x.  7   4096 Jan 20 16:13 hiawatha
lrwxrwxrwx.  1      8 Jan 20 16:01 hiawatha-7.4 -> hiawatha
drwxrwxr-x.  2   4096 Jan 21 18:03 indexer
-rw-rw-r--.  1   1894 Jan 21 19:45 INSTALL
drwxrwxr-x. 14   4096 Jan 21 17:55 mediawiki-1.16.1-sa
-rw-rw-r--.  1   1155 Jan 21 15:48 README
-rw-rw-r--.  1 210437 Jan 20 15:41 test_article.xml
lrwxrwxrwx.  1     14 Jan 19 21:55 wiki-splits -> wiki-splits-es
drwxrwxr-x. 19 266240 Jan 19 20:39 wiki-splits-en
drwxrwxr-x.  3 237568 Jan 19 22:11 wiki-splits-es
drwxrwxr-x.  4  12288 Jan 21 17:20 wiki-splits-tl
```

```
#  If you have downloaded an index compatible with this software, pat
# yourself on the back!  Otherwise, you are now ready to run the indexer
# on your dump.  You may have to count to 3,000,000.  The index can be
# validated immediately, if you want to verify the process is going along
# smoothly.  Hint: try an article beginning in "A".
```

```
    cd indexer ; make index
```


## SERVE THE PAGES ##

> You should have received a bundle including a portable web server for your platform.  Or, you can run your own just as well.  Follow the instructions below and head a browser to port `http://127.0.0.1/8000`

> You are now running the same software as da Big One, not an imitation!

> If you need to install a web server, pick one capable of last-updated caching and php cgi.  FastCGI support is easy and will make you happy.  For example, to install "hiawatha":

```
wget http://www.hiawatha-webserver.org/files/hiawatha-7.4.tar.gz
tar xzf hiawatha-7.4.tar.gz
cd hiawatha-7.4
./configure --prefix=`pwd`/../hiawatha/ --disable-ipv6 --disable-ssl --disable-xslt && make

cd wikipedia-offline-patch/
vi config/hiawatha.conf
  # :%s/WebsiteRoot/<MEDIAWIKI DIR>/g
cp config/hiawatha.conf hiawatha/etc/hiawatha/

# run a FastCGI server.  Otherwise, edit the conf file to disable.
php-cgi -b 2005 < /dev/null &


# Start hiawatha (running on port 8000 by default)

    ./hiawatha/sbin/hiawatha
```

> Or, to use another web server such as Apache, edit your config and add:
```
DocumentRoot  mediawiki-1.16.1-sa/

<Directory /<ABSOLUTE_PATH>/wikipedia-offline-patch/mediawiki-1.16.1-sa>
  # enable the rewriter
  RewriteEngine On
  RewriteBase /wiki
  # anything under /wiki is treated as an article title, unless it is a file
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteRule ^/(.+)$ index.php?title=$1 [PT,L,QSA] 
</Directory>
```