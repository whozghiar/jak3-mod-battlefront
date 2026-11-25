("CTYPESC.DGO"
 ("roboguard-city.o"
  "spydroid.o"
  "flying-turret.o"
  "tpage-1244.go"
  ;; MOD battlefront -- art groups sorted by decreasing size: once the first art group logs in,
  ;; each DGO buffer shrinks to the object it held + 2 KB, and the object two slots later must fit
  ;; in it (see docs/modding/current_mod/battlefront_readme.md). The two bf-hover art groups are
  ;; the jetpack guards drawn on the flying-turret code (build-actor, Jak 2 model; blue = Freedom
  ;; League textures).
  "bf-baron-ag.go"         ;; 1084384, Baron Praxis (round 44, build-actor, Jak 2 model; round 46's clips)
  "bf-ashelin-ag.go"       ;; 313296, Ashelin (round 53, build-actor, Jak 3 model, clips made at install; round 55 Jak's moves; round 56 throw, captured kick, pistol whip, jump kick, reload)
  "roboguard-city-ag.go"   ;; 116080
  "bf-hover-red-ag.go"     ;; 78208
  "bf-hover-blue-ag.go"    ;; 78208
  "spydroid-ag.go"         ;; 62832
  "bf-spider-blue-ag.go"   ;; 20832, the Freedom League's spider robot (round 46, build-actor, recolored)
  "kg-flying-turret-ag.go" ;; 14992
  "bf-robot-blue-ag.go"    ;; 8816, the Freedom League's robotguard (round 46, build-actor, recolored)
  "kg-debris-ag.go"        ;; 7520
  "ctypesc.go"
 ))
