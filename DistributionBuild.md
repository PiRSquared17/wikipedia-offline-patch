# Windows #

```
get [php vc9] (be sure to match xapian build), [xapian] [zlib] [msvc runtime 2008]
cp php_xapian.dll php/ext/
cp xapian.php mediawiki/includes/
php.ini:
 extension php_xapian.dll
 extension php_bz2.dll
 ;include_dir ABS
```