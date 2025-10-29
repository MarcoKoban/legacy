Documentation – Choix technologiques du projet
1. Choix du langage Python pour le back-end

Même si le passage en Python est imposé par le contexte du projet, plusieurs arguments techniques et stratégiques rendent ce choix particulièrement pertinent :

a) Lisibilité et maintenabilité

Python privilégie une syntaxe claire, concise et proche du langage naturel, facilitant la relecture et la maintenance du code, même par des personnes non expertes.

b) Large écosystème

Python dispose d’une immense bibliothèque standard et d’innombrables modules externes (PyPI), couvrant aussi bien :

le traitement de données (pandas, numpy)

l’IA/ML (scikit-learn, PyTorch, TensorFlow)

le web (Django, Flask, FastAPI)

la visualisation (matplotlib, seaborn).

Cela permet de répondre rapidement à de nouveaux besoins sans réinventer la roue.

c) Interopérabilité et intégration

Python est facilement interopérable avec d’autres langages (C, C++, Java) via des bindings, et avec des API externes.

Il est donc adapté pour reprendre des modules existants, ou interagir avec des services web modernes.

d) Courbe d’apprentissage faible

Comparé à OCaml, Python est beaucoup plus accessible pour une grande communauté de développeurs.

Cela facilite la montée en compétence de nouvelles personnes sur le projet, réduit le coût de formation, et assure une meilleure pérennité.

e) Pérennité et communauté

Python est aujourd’hui l’un des langages les plus populaires au monde (classements TIOBE, StackOverflow Developer Survey).

La communauté active garantit un suivi à long terme, de la documentation abondante, et des solutions aux problèmes courants.

2. Choix du framework Angular pour le front-end

Pour la partie front-end, plusieurs frameworks modernes existent (React, Vue.js, Svelte, etc.). Le choix d’Angular se justifie par plusieurs critères techniques, organisationnels et stratégiques.

a) Structure et opinion forte

Angular est un framework complet (contrairement à React ou Vue qui sont principalement des bibliothèques de rendu).

Il impose une architecture claire (modules, composants, services) qui force de bonnes pratiques de structuration du code.

Cela rend les gros projets plus faciles à maintenir, car toute l’équipe suit le même modèle.

b) Écosystème intégré

Angular intègre nativement :

un moteur de templating

un système de routing

un système de formulaires et de validation

un support RxJS (programmation réactive)

un outil CLI très puissant pour la génération de code, le build et les tests.

Contrairement à React ou Vue, il n’est pas nécessaire d’assembler plusieurs bibliothèques externes pour avoir un projet complet et robuste.

c) Maintenu par Google et utilisé en entreprise

Angular est développé et maintenu par Google, avec un cycle de release clair et une roadmap stable.

Beaucoup de grandes entreprises l’utilisent pour des applications critiques (banques, santé, administrations), ce qui renforce la crédibilité et la stabilité à long terme.

d) Idéal pour les projets de grande envergure

Là où Vue et Svelte sont excellents pour des projets légers et réactifs, Angular est particulièrement adapté à des applications complexes qui nécessitent :

une forte modularité

une gestion stricte des dépendances

des fonctionnalités avancées dès le départ.

e) TypeScript intégré

Angular est basé sur TypeScript, ce qui permet :

un typage statique (réduction des bugs à l’exécution)

une meilleure autocomplétion et documentation dans les IDE

une plus grande robustesse et maintenabilité sur le long terme.

React et Vue peuvent utiliser TypeScript, mais ce n’est pas natif ni obligatoire, ce qui mène parfois à des incohérences dans les projets.

f) Comparaison avec les alternatives

React : très flexible et populaire, mais nécessite d’assembler de nombreux outils tiers (Redux, React Router, etc.) → risque d’incohérence entre projets.

Vue.js : léger et simple à prendre en main, mais moins structurant pour de très gros projets et encore moins utilisé dans les grandes entreprises que React ou Angular.

Svelte : innovant et performant, mais encore jeune, avec une communauté et un écosystème plus limités.

Dans notre cas, le besoin est un projet robuste, maintenable, structuré et évolutif, ce qui correspond parfaitement aux points forts d’Angular.

3. Conclusion

Le choix de Python pour le back-end et Angular pour le front-end s’explique par un compromis entre :

accessibilité et popularité (facilité d’apprentissage, communauté)

robustesse et maintenabilité (structure imposée, typage, long terme)

richesse de l’écosystème (bibliothèques disponibles, intégration facile)

En somme :

Python apporte la simplicité et la flexibilité nécessaires côté serveur.

Angular garantit une architecture claire et évolutive côté client, ce qui est essentiel pour assurer la pérennité du projet.