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
  "roboguard-city-ag.go"   ;; 116080
  "bf-hover-red-ag.go"     ;; 78208
  "bf-hover-blue-ag.go"    ;; 78208
  "spydroid-ag.go"         ;; 62832
  "kg-flying-turret-ag.go" ;; 14992
  "kg-debris-ag.go"        ;; 7520
  "ctypesc.go"
 ))
