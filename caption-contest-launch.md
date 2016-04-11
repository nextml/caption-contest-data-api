## List of what to do when launching a New Yorker caption contest:
### round 1
0. Launch an machine. Be sure to include a `--instance-type=c3.8xlarge` flag! I
   typically do this the night before because it takes a while.
1. Copy and paste the folder from the last week
    * Copy the new input (captions, comic file) across.
    * In copying the caption file across, there can be an issue with newlines.
      In vim, I have to run the command `:%s/\r/\r/g` to fix this (which just
      replaces `\r` with `\r`, I'm not sure why it works.
    * Single and double quotes (`'` and `"`) are okay in captions. I've tested
      both and I see both appear in the captions.
2. Run `experiment_cardinal.py` (changing `TARGET_FILE`, `COMIC_FILE`).
    * This will automatically count the number of captions for you and ask for
      a response.
3. (optional) scp the query page up. An example shown is shown at [1]. The query page is
   at [2] then `query_page/query_page` replaced with `query_page/caption_507.html`
4. Test. Send an email out, etc.
5. Setup redirects at nextml.org/captioncontest, nextml.org/captioncontest_dashboard
    * The dashboard link can never change
    * The query URL will only change with exp_uid and exp_key
6. Publish these results (send an email out)

``` shell
[1]:scp -i $KEY_FILE newyorkercaption.html ubuntu@ec2-52-89-3-26.us-west-2.compute.amazonaws.com:/usr/local/next-discovery/next/query_page/templates/newyorkercaption.html
[2]:http://ec2-52-89-236-176.us-west-2.compute.amazonaws.com:8000/query/query_page/caption_dual_507/602f4f48d4ac1d2bb099644e0deb77/fa17bf7f7d6bab302b8b06a29dba38
```


### round 2
* run files for both experiments (launch both experiments; query pages don't
  matter. Only `caption_dual.html` matters (links to both experiments))
* in `caption_dual_507_done_button.html`, note the following
  * Change `exp_uid`, exp_key below!
  * `exp_key` is misnamed as widget_key
  * Change N on line 47 and 123 (there are notes in `newyorkercaption.html`
    that detail this more; I tried to include notes in each file of what needed
    to be changed.
  * Do `CardinalBandits` first, the `DuelingBandits`

