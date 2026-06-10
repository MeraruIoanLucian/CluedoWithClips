;;; Murder Mystery Puzzle Solver - Reguli CLIPS

;;; Templateuri

(deftemplate suspect
   (slot name (type STRING)))

(deftemplate weapon
   (slot name (type STRING)))

(deftemplate location
   (slot name (type STRING)))

;;; combinatie (suspect, arma, locatie)
(deftemplate possible
   (slot suspect (type STRING))
   (slot weapon (type STRING))
   (slot location (type STRING)))

;;; solutia gasita
(deftemplate solution
   (slot suspect (type STRING))
   (slot weapon (type STRING))
   (slot location (type STRING)))

;;; daca nu avem solutie
(deftemplate no-solution)

;;; Indicii

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


;;; Eliminare

;;; Suspectul X NU a folosit arma Y
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
(defrule apply-suspect-in-location
   (declare (salience 50))
   (clue-suspect-location (suspect ?s) (location ?l))
   ?p <- (possible (suspect ?s) (location ?l2&~?l))
   =>
   (retract ?p))

;;; Arma Y ERA in locatia Z
(defrule apply-weapon-in-location
   (declare (salience 50))
   (clue-weapon-location (weapon ?w) (location ?l))
   ?p <- (possible (weapon ?w) (location ?l2&~?l))
   =>
   (retract ?p))


;;; Detectarea solutiei

;;; a ramas o singura varianta
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

;;; nu mai avem variante posibile
(defrule no-solution-found
   (declare (salience 5))
   (not (possible))
   (not (solution))
   (not (no-solution))
   =>
   (assert (no-solution))
   (printout t "=== EROARE: Nu s-a gasit nicio solutie! ===" crlf)
   (printout t "Indiciile sunt contradictorii." crlf))
