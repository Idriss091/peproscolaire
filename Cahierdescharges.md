1. Présentation du projet
Nom du projet : PeproScolaire
PeproScolaire est une application web pensée pour les établissements scolaires du
second degré (collèges et lycées), avec pour objectif de simplifier la gestion quotidienne
de la vie scolaire tout en introduisant des innovations basées sur l’intelligence
artificielle.
Le logiciel reprend toutes les fonctionnalités classiques que l’on retrouve dans des
solutions comme Pronote ou Vie Scolaire (Axess) : gestion des emplois du temps, cahier
de textes, saisie des notes, bulletin, suivi des absences, messagerie interne. Mais
PeproScolaire va plus loin. Il est conçu pour être plus intuitif, plus intelligent et mieux
adapté aux besoins réels des enseignants, des élèves et de l’administration.
En tant qu’enseignant, j’ai pu observer les limites des outils existants, notamment leur
lourdeur d’utilisation et leur manque d’ergonomie. PeproScolaire se veut à la fois plus
moderne et plus humain, avec une interface fluide, un accès rapide à l’essentiel, et des
outils intelligents pour gagner du temps au quotidien.
Convaincu que le futur ne pourra se faire sans l’IA, le logiciel intègre des modules IA
concrets et utiles : génération automatique d’appréciations à partir des notes et du profil
de l’élève, analyse des performances par classe ou par élève avec des suggestions
pédagogiques, assistant de révision personnalisé pour les élèves, chatbot éducatif, ou
encore détection des signaux faibles en cas de décrochage ou d’absentéisme inhabituel.
Une autre dimension importante que nous avons souhaité inclure est celle de
l’orientation et de l’insertion professionnelle. PeproScolaire proposera également un
module d’accompagnement à la recherche de stages, en mettant à disposition des
élèves des offres locales, un générateur de lettre de motivation assisté par IA, un suivi
des candidatures et des alertes automatisées pour les élèves en difficulté.
Notre ambition est de faire de PeproScolaire non seulement un outil administratif, mais
aussi un véritable partenaire pédagogique, au service de la réussite des élèves et du
confort de travail des enseignants.
2. Hébergement et déploiement du logiciel
2.1 Hébergement centralisé en mode SaaS (conseillé)
PeproScolaire sera hébergé en tant que plateforme SaaS (Software as a Service). Cela
signifie que tout le logiciel est installé sur un serveur central, et que chaque
établissement scolaire accède à son espace dédié via un sous-domaine personnalisé.
Par exemple, un lycée pourrait accéder à son espace via une adresse comme :
https://lycee-morvan.peproscolaire.fr.
Ce modèle permet de mutualiser les ressources et de faciliter la maintenance.
Concrètement, lorsqu’un établissement souhaite utiliser PeproScolaire, nous créons
pour lui :
• Un sous-domaine personnalisé
• Une base de données dédiée (ou un espace logique séparé dans une base
partagée)
• Une interface personnalisée (logo, couleurs, nom de l’établissement)
Les données des utilisateurs (professeurs, élèves, parents, administration) sont
hébergées sur des serveurs sécurisés localisés en France, afin de respecter la
réglementation RGPD. Toutes les communications sont chiffrées via HTTPS.
Les technologies recommandées pour construire cette infrastructure sont les suivantes
:
• Backend : Django (Python) ou Node.js
• Frontend : Vue.js ou React
• Base de données : PostgreSQL
• IA : Python avec scikit-learn et Transformers pour les modules intelligents
• Hébergement : OVHcloud ou Scaleway
Une fois en place, chaque établissement n’a besoin d’aucune compétence technique
pour gérer la plateforme. Les mises à jour, la sécurité, les sauvegardes et les évolutions
fonctionnelles sont toutes centralisées.
Ce modèle est actuellement le plus adapté aux réalités des lycées français, car la
majorité des établissements ne peuvent pas héberger ni intégrer eux-mêmes une
solution complexe. De plus, la plupart des logiciels concurrents (Pronote, Vie Scolaire...)
fonctionnent déjà sur ce principe.
3. Interface – Navigation et fonctionnalités clés
Le point d’entrée de PeproScolaire est une sélection du profil sur la page d’accueil,
permettant à chaque utilisateur (élève, parent, professeur) d’accéder à son espace
respectif. Une fois connecté, le professeur est redirigé vers un tableau de bord
personnel.
 Figure 1a : Point d’entrée Vie scolaire
 Figure 1b : Quand on clique sur “Professeurs”
On va maintenant passer à ce que doit obligatoirement contenir le logiciel pour être
crédible : messages non lus, cours du jour, absences à saisir, devoirs à corriger, etc. Le
menu de gauche permet de naviguer facilement entre les différentes rubriques : emploi
du temps, cahier de textes, évaluations, vie scolaire, messagerie, dossier élève et
paramètres. L’objectif est que la plateforme soit simple et ergonomique, le mieux est
l’ennemi du bien.
• Accueil : Sur cette page, nous avons accès aux actualités de l’établissement, le
chatbot (partie suivante) ...
• Emploi du temps : Le professeur peut consulter son propre emploi du temps,
celui des élèves (sélectionner la classe puis l’élève), des classes et même des
salles. La vue est hebdomadaire, claire, avec la possibilité d’exporter ou de
naviguer dans le temps.
 Figure 2a : Emploi du temps des classes
Figure 2b : Emploi du temps des élèves
• Cahier de textes : Permet de déclarer le contenu du cours et le travail à faire. Bien
que cette fonctionnalité existe dans Vie Scolaire, elle manque de fluidité ;
PeproScolaire proposera une version simplifiée, avec des suggestions
automatiques de contenu, et un rappel IA aux élèves.
 Figure 3a : Cahier de textes – Vue calendaire
Figure 3b – Cahier de textes
Pour moi cette partie manque clairement d’ergonomie pour le professeur.
D’ailleurs encore actuellement je n’y comprends pas grand chose. Il faut
proposer autre chose.
Figure 3c – Suggestion triviale
• Vie scolaire : Cette rubrique permet d’enregistrer les absences, retards,
sanctions. Lorsqu’un cours débute, la liste des élèves apparaît automatiquement
pour la saisie de l’appel. On peut choisir la date, la classe. PeproScolaire
proposera un affichage optimisé et des alertes intelligentes (élève
fréquemment absent, retard chronique, etc.).
 Figure 4 – Gestion des absences
• Évaluations : Le professeur peut saisir les notes, affecter des coefficients,
visualiser les moyennes, et suivre l’évolution des élèves. L’interface est propre,
avec des colonnes par devoir. PeproScolaire y intégrera un module IA pour
analyser les performances et suggérer des remédiations ou des groupes de
besoin.
 Figure 5a – Notes et compétences
Figure 5b - Appréciations
Figure 5c – Conseil de classe
Pour la partie conseil de classe, je ne peux rien modifier. Seul le professeur
principal le peut. Ceci implique une disjonction de cas lorsque le logiciel sera
implémenté.
• Dossier élève : Accès aux informations administratives, vie scolaire, résultats et
parents. L’interface actuelle est claire mais rigide ; PeproScolaire proposera une
vue plus synthétique avec des alertes personnalisées.
Figure 6 – Dossier élève
• Messagerie : Les professeurs peuvent communiquer avec les élèves et les
parents. Ils ont accès aux messages reçus, envoyés, aux brouillons et à la
corbeille. C’est un outil central pour le suivi. L’IA pourra à terme aider à classer
les messages urgents ou à proposer des réponses types. Chaque message peut
être redirigé automatiquement vers une adresse e-mail choisie par l’utilisateur.
Figure 7 - Messagerie
• Notifications : Un système d’alerte non intrusif permet d’être informé dès qu’un
événement pertinent a lieu (nouveau message, retard à enregistrer, devoir non
corrigé...). Ces notifications apparaissent dans une barre latérale dédiée
accessible en haut à droite.
• Paramètres du compte : Le professeur peut modifier son mot de passe, gérer ses
préférences, ou rediriger ses messages vers son adresse e-mail personnelle.
Cette redirection se fait en quelques clics depuis la rubrique "Mon compte".
• Déconnexion : Accessible en haut à droite, elle redirige directement vers l’écran
de connexion initial, propre et épuré.
Ceci est l’interface professeur mais évidemment, l’interface élève et celle des parents
sont pratiquement similaires. Les concernant, les priorités sont de : voir l’emploi du
temps, accéder aux devoirs, aux notes et pouvoir communiquer avec les professeurs.
4. Fonctionnalités innovantes proposées par Pepro
4.1 Suggestion intelligente de devoirs
Pepro intègre une fonctionnalité inédite de suggestion de devoirs assistée par
intelligence artificielle. Lorsqu’un professeur remplit son cahier de textes ou prépare son
cours, il peut préciser la notion étudiée ou le chapitre couvert(ex. : "Fonctions affines",
"Révolution française", "Les atomes et les ions"). À partir de ces éléments, Pepro
propose automatiquement plusieurs devoirs types adaptés au niveau de la classe
(exercice simple, QCM, rédaction guidée, etc.).
Le professeur peut :
• Sélectionner un devoir parmi les suggestions,
• en éditer le contenu directement,
• ou le rejeter et créer manuellement un autre exercice.
Ces suggestions sont générées à partir d’une base pédagogique constamment enrichie,
croisée avec les pratiques de l’établissement et les devoirs antérieurement donnés dans
la classe. Cela permet :
• un gain de temps pour l’enseignant,
• une homogénéisation des devoirs d’un même niveau,
• et à terme, une adaptation fine aux profils des élèves (ex. : renforcement
personnalisé).
Cette fonctionnalité ouvre la voie vers une pédagogie augmentée, où l’intelligence
artificielle vient soutenir le jugement professionnel du professeur sans jamais le
remplacer.
Peut-être un partenariat avec un grand éditeur de manuels scolaires ?? Utilisation
libre la première année puis un pourcentage reversé les années suivantes ??
4.2 Génération intelligente d’appréciations pour les bulletins
Lors de la saisie des bulletins, Pepro propose automatiquement des appréciations
personnalisées pour chaque élève, en s’appuyant sur plusieurs sources d’information
disponibles dans le système : les notes trimestrielles, l’évolution de l’élève, les
absences ou retards éventuels, et les commentaires renseignés par le professeur au
cours de l’année.
Le fonctionnement est simple : pour chaque élève, Pepro génère une ou plusieurs
suggestions d’appréciation en langage naturel (ex. : "Élève impliqué et sérieux. Les
résultats sont solides et le comportement en classe est exemplaire."). Le professeur a
ensuite la possibilité de :
• valider directement l’appréciation proposée,
• la modifier partiellement,
• ou demander une reformulation (ex. plus bienveillante, plus ferme, plus courte,
etc.).
Le modèle IA peut s’adapter progressivement au style d’écriture du professeur, en
tenant compte des appréciations validées dans les bulletins précédents.
L’objectif est triple :
• Réduire la charge mentale liée à la rédaction répétitive de dizaines
d’appréciations,
• Maintenir une cohérence et une richesse de formulation tout au long du
bulletin,
• Favoriser des retours constructifs pour les élèves et les familles, même dans
les cas complexes (élève en difficulté, comportement irrégulier, etc.).
4.3 Détection des élèves à risque de décrochage scolaire (par IA)
PeproScolaire propose un système d’analyse prédictive destiné à repérer de manière
précoce les élèves en voie de décrochage. Grâce à un modèle d’intelligence artificielle,
le logiciel peut croiser plusieurs indicateurs discrets pour alerter les équipes éducatives
lorsqu’un élève montre des signes de fragilité.
Les signaux pris en compte incluent :
• la fréquence et la récurrence des absences ou retards,
• une baisse significative ou continue des résultats,
• une absence de remise de devoirs ou d’interactions pédagogiques,
• un manque de communication ou des tensions avec les équipes (ex. absence de
réponse aux messages),
• des variations inhabituelles dans le comportement signalé par les professeurs ou
la vie scolaire.
Ces données permettent au système d’attribuer un score de vigilance à chaque élève.
Lorsque ce score dépasse un seuil défini, une alerte est transmise au professeur
principal, au CPE ou à la direction.
Un tableau de bord visuel permet de suivre ces signaux, d’identifier les élèves les plus
vulnérables et d’agir en conséquence (entretien, signalement, soutien). Cette approche
vise à :
• anticiper le décrochage,
• orienter les ressources humaines là où elles sont nécessaires,
• justifier les interventions par des données objectives et consolidées.
4.4 Chatbot pédagogique pour les élèves
PeproScolaire intègre un assistant conversationnel intelligent destiné aux élèves.
Accessible depuis leur espace personnel, ce chatbot pédagogique permet aux élèves
de poser des questions à tout moment sur les notions étudiées en classe, les devoirs à
faire ou les méthodes à appliquer.
L’élève peut :
• interroger le chatbot sur une notion (ex. "comment factoriser une expression ?"),
• demander une reformulation ou un exemple plus simple d’un devoir donné,
• recevoir des conseils pour s’organiser dans ses révisions,
• obtenir des rappels automatisés sur les échéances à venir.
Le chatbot est connecté au cahier de textes et aux devoirs renseignés par les
professeurs, ce qui lui permet de proposer une aide contextuelle pertinente et à jour. Il
peut aussi suggérer des ressources complémentaires (liens, exercices interactifs,
résumés).
L’objectif est de :
• rendre l’élève plus autonome dans son apprentissage,
• offrir un accompagnement continu, même en dehors des horaires scolaires,
• soulager les enseignants des nombreuses questions répétitives ou logistiques,
• renforcer la continuité pédagogique pour les élèves absents ou en difficulté
ponctuelle.
4.5 Module de suivi des stages
PeproScolaire intègre un module entièrement dédié à la gestion et au suivi des stages
obligatoires (notamment en classe de 3e, seconde, ou BTS). Ce module permet à la fois
aux élèves de gérer leur recherche et à l’établissement d’assurer un suivi administratif
clair et centralisé.
Fonctionnalités pour les élèves :
• Ajout d’entreprises ciblées et suivi des candidatures (envoyé / accepté / refusé),
• Téléversement de la convention signée et des documents demandés,
• Saisie d’un journal de bord ou de notes liées au stage,
• Dépôt final du rapport de stage.
Fonctionnalités pour les enseignants ou référents :
• Suivi en temps réel de la situation de chaque élève,
• Liste des conventions validées / manquantes,
• Possibilité de laisser des commentaires ou d’émettre des rappels,
• Génération de listes ou de rapports d’état pour le chef d’établissement.
Ce module facilite considérablement le travail des professeurs principaux ou
responsables de niveau. Il permet également aux familles d’avoir un point de repère
unique et d’éviter les oublis ou pertes de documents.
L’objectif est de :
• structurer la démarche de recherche de stage dès le collège,
• aider l’élève à gagner en autonomie et en professionnalisme,
• renforcer le lien entre école et monde professionnel,
• éviter les pertes de temps dans les relances manuelles et garantir une
traçabilité claire.
4.6 Planificateur intelligent de devoirs
PeproScolaire inclut un système de planification intelligent conçu pour éviter la
surcharge de travail chez les élèves. Lorsqu’un professeur souhaite planifier un devoir,
le logiciel analyse la charge de travail déjà prévue pour cette classe sur la période
visée.
Fonctionnement :
• Lors de la saisie d’un devoir, Pepro affiche un aperçu des devoirs déjà
programmés pour les jours suivants.
• Si plusieurs devoirs ou évaluations sont concentrés sur une même journée, une
alerte douce est proposée au professeur avec la possibilité de décaler le devoir.
• Les élèves disposent d’un calendrier clair de leur charge de travail par semaine,
leur permettant de mieux s’organiser.
Cette fonctionnalité vise à :
• répartir de manière équitable les devoirs entre les matières,
• éviter les pics de stress ou de fatigue liés à l’accumulation des évaluations,
• renforcer la coordination pédagogique au sein des équipes enseignantes,
• favoriser une organisation plus sereine du travail scolaire pour les élèves
comme pour les familles.
4.7 Générateur intelligent d’évaluations personnalisées avec barème
détaillé
📘Fonction :
PeproScolaire propose un outil permettant aux professeurs de générer
automatiquement des évaluations (contrôles, devoirs, QCM, rédactions...) adaptées
aux notions étudiées en classe, avec un barème finement détaillé et une correction
complète générée à partir des attendus pédagogiques.
⚙️ Comment ça marche :
• Le professeur entre :
o la classe concernée (ex : 2nde),
o le chapitre étudié (ex : “Fonctions affines”),
o le type d’évaluation souhaité (QCM, exercice classique, rédaction, etc.),
o la durée prévue (ex : 45 min).
• Pepro génère automatiquement :
o un sujet complet, structuré par niveaux de difficulté,
o un barème détaillé par question (et même par sous-partie ou argument,
si souhaité),
o une correction complète justifiée et claire, utilisable comme base de
correction ou de support pédagogique.
• L’enseignant peut modifier ou enrichir la proposition avant validation.
🧠Exemple concret :
Pour un chapitre de SVT sur la mitose :
• Pepro génère un exercice avec schéma à annoter, un QCM et une question de
rédaction.
• Le barème prévoit 1 pt pour chaque bonne annotation du schéma, 0.5 pt pour
chaque bonne réponse au QCM, et 5 pts pour la rédaction avec des points
attribués à chaque argument (définition, étapes, conclusion).
🎯 Objectif :
• Gagner du temps dans la conception d’évaluations,
• Garantir l’équité et la cohérence des barèmes,
• Proposer une base pédagogique solide pour le retour aux élèves,
• Donner des corrigés réutilisables en classe ou en révision.
Ce générateur peut être enrichi à partir de banques d'exercices validées par des
enseignants, ou de ressources publiques, pour garantir la qualité pédagogique.
Conclusion
La dernière partie est importante c’est par elle que PeproScolaire se distingue des autres
logiciels classiques mais la première l’est tout autant car le logiciel se doit d’être robuste
et fiable, au moins autant que les autres. Les idées proposées ne sont pas toutes au
même degré d’importance, de la plus importante à la moins importante : détection des
décrochages scolaires, remplissage des bulletins pour les professeurs, générateur
d’évaluations personnalisées, suggestion de devoirs, chatbot avec les élèves, module
de suivi des stages (2nde et 3ème), planificateur intelligent de devoirs.
Ainsi s’achève ce cahier des charges.