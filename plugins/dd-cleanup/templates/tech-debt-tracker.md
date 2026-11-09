# Tech debt tracker

Maintained by dd-cleanup and by humans. The cleanup agent reads this before every run and skips
anything listed under Deferred or Won't fix. Move an item to Won't fix to stop it being re-raised.

## Recheck (likely dead, logging added)
<!-- - [ ] <symbol> (<path>) - log added <date>, recheck: <date> -->

## Deferred (too big or risky for an automatic PR)
<!-- - [ ] <category>: <description> (<paths>) - found <date> -->

## Tool config (false positives to whitelist by hand)
<!-- - [ ] knip/vulture flags <symbol> but it is used via <how> -->

## Won't fix
<!-- - <description> - reason -->
