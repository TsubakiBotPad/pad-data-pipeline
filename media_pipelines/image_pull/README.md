# Image assets

This directory contains scripts to pull/process/clean PAD full monster and portrait images.

See the individual scripts for details. The padtools library, Kiootic's animated image parser, and the processed PAD
data files are necessary dependencies for various scripts.

## Hosted assets

I'm hosting this data on Google Cloud Storage and on Backblaze. The Cloud Storage buckets these are published to is
locked down to prevent scraping, and Backblaze isn’t really sync-friendly; contact tactical_retreat if you would like to
sync anything here.

When possible, please use the Backblaze links, it costs me less money.

## Portraits

Server is one of [na, jp]

`https://f002.backblazeb2.com/file/miru-data/padimages/<server>/portrait/<id>.png`

It is a bit harder to set up your own extract for this; it requires access to the processed PAD data files for NA/JP to
get the portrait colors.

## Full Images

Server is one of [na, jp]

`https://f002.backblazeb2.com/file/miru-data/padimages/<server>/full/<id>.png`

It is relatively easy to set up your own extract for this.

## HQ Images

`https://storage.googleapis.com/mirubot/padimages/hq_images/<id>.png`

There are only a few hundred of these, they’re scraped weekly from GungHo’s site. Scraping this takes forever, there’s
no index published so you have to try every URL.

## Animated Images

```
https://f002.backblazeb2.com/file/miru-data/padimages/animated/<id>.gif
https://f002.backblazeb2.com/file/miru-data/padimages/animated/<id>.mp4
```

These are also published to Cloud Storage, but they’re large and CS is expensive compared to Backblaze. If you would
like access to sync them, contact tactical_retreat.

The extract script requires Kiootic’s animated image parser.
