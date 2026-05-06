;;;======================================================
;;; Murder Mystery Puzzle Solver - Reguli CLIPS
;;; Sistem expert bazat pe eliminare pentru rezolvarea
;;; puzzle-urilor de tip murder mystery.
;;;
;;; Combinatiile posibile sunt generate de Python si
;;; incarcate ca fapte. CLIPS le elimina pe baza indiciilor.
;;;======================================================

;;; ===== TEMPLATE-URI =====

(deftemplate suspect
   (slot name (type STRING)))

(deftemplate weapon
   (slot name (type STRING)))

(deftemplate location
   (slot name (type STRING)))

;;; O combinatie posibila (suspect, arma, locatie)
(deftemplate possible
   (slot suspect (type STRING))
   (slot weapon (type STRING))
   (slot location (type STRING)))

;;; Solutia gasita
(deftemplate solution
   (slot suspect (type STRING))
   (slot weapon (type STRING))
   (slot location (type STRING)))

;;; Indicator ca nu s-a gasit solutie
(deftemplate no-solution)

;;; ===== INDICII (CLUES) =====

(deftemplate clue-not-suspect-weapon
   (slot suspect (type STRING))
   (slot weapon (type STRING)))

(deftemplate clue-not-suspect-location
   (slot suspect (type STRING))
   (slot location (type STRING)))

(deftemplate clue-not-weapon-location
   (slot weapon (type STRING))
   (slot location (type STRING)))

(deftemplate clue-suspect-location
   (slot suspect (type STRING))
   (slot location (type STRING)))

(deftemplate clue-weapon-location
   (slot weapon (type STRING))
   (slot location (type STRING)))


;;; ===== REGULI DE ELIMINARE =====

;;; Suspectul X NU a folosit arma Y
;;; Elimina toate combinatiile cu suspectul X si arma Y
(defrule eliminate-not-suspect-weapon
   (declare (salience 50))
   (clue-not-suspect-weapon (suspect ?s) (weapon ?w))
   ?p <- (possible (suspect ?s) (weapon ?w))
   =>
   (retract ?p))

;;; Suspectul X NU era in locatia Y
(defrule eliminate-not-suspect-location
   (declare (salience 50))
   (clue-not-suspect-location (suspect ?s) (location ?l))
   ?p <- (possible (suspect ?s) (location ?l))
   =>
   (retract ?p))

;;; Arma Y NU era in locatia Z
(defrule eliminate-not-weapon-location
   (declare (salience 50))
   (clue-not-weapon-location (weapon ?w) (location ?l))
   ?p <- (possible (weapon ?w) (location ?l))
   =>
   (retract ?p))

;;; Suspectul X ERA in locatia Y
;;; Elimina toate combinatiile unde suspectul X e in alta locatie
(defrule apply-suspect-in-location
   (declare (salience 50))
   (clue-suspect-location (suspect ?s) (location ?l))
   ?p <- (possible (suspect ?s) (location ?l2&~?l))
   =>
   (retract ?p))

;;; Arma Y ERA in locatia Z
;;; Elimina toate combinatiile unde arma Y e in alta locatie
(defrule apply-weapon-in-location
   (declare (salience 50))
   (clue-weapon-location (weapon ?w) (location ?l))
   ?p <- (possible (weapon ?w) (location ?l2&~?l))
   =>
   (retract ?p))


;;; ===== DETECTARE SOLUTIE =====

;;; Daca a ramas o singura combinatie posibila
(defrule found-solution
   (declare (salience 10))
   (possible (suspect ?s) (weapon ?w) (location ?l))
   (not (possible (suspect ~?s)))
   (not (possible (weapon ~?w)))
   (not (possible (location ~?l)))
   (not (solution))
   =>
   (assert (solution (suspect ?s) (weapon ?w) (location ?l)))
   (printout t "=== SOLUTIE GASITA ===" crlf)
   (printout t "Criminal: " ?s crlf)
   (printout t "Arma: " ?w crlf)
   (printout t "Locatia: " ?l crlf))

;;; Daca nu mai exista combinatii posibile
(defrule no-solution-found
   (declare (salience 5))
   (not (possible))
   (not (solution))
   (not (no-solution))
   =>
   (assert (no-solution))
   (printout t "=== EROARE: Nu s-a gasit nicio solutie! ===" crlf)
   (printout t "Indiciile sunt contradictorii." crlf))
