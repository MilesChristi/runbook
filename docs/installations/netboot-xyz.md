#Implémentation D'outils et autres sur PXE

L’implémentation **d’outils en PXE** via FOG transforme un simple serveur d’imagerie en plateforme centralisée de **maintenance, de déploiement et de récupération**.

## Netboot.xyz

netboot.xyz est une plateforme PXE réseau universelle qui permet de démarrer un large choix d’outils, d’ISO et de systèmes d’exploitation directement depuis le réseau, sans avoir besoin de supports physiques.

**Ce que netboot.xyz fait**

netboot.xyz sert à remplacer ou compléter la chaîne PXE classique comme :

- FOG iPXE

- Serveurs PXE Linux

- Serveurs WDS/Windows

Il propose un menu interactif très riche et adaptable qui peut charger :

- Installateurs Linux (Ubuntu, Debian, Fedora…)

- Outils de maintenance (SystemRescue, MemTest, test réseau…)

- Utilitaires (GParted, Parted Magic, Clonezilla…)

- Boot Windows via des installateurs ou WinPE

- Options de récupération réseau

Tout cela **via iPXE**, sans ISO locale sur la machine cliente.

**Comment ça marche**

1. Le client démarre en PXE.

2. Il charge le binaire iPXE depuis le serveur.

3. iPXE télécharge et affiche le menu netboot.xyz.

4. Tu choisis un outil dans le menu.

5. netboot.xyz charge le noyau/initrd ou chaîne vers l’ISO sur Internet.

**Résumé simple**

**netboot.xyz = une collection PXE universelle de menus + chaînes de boot pour presque tous les systèmes et outils réseau.**

C’est léger, évolutif, indépendant des ISO physiques, et idéal pour les environnements multi-outils comme FOG.

### 1) Télécharger netboot.xyz (UEFI + Legacy) sur le serveur FOG

```bash
cd /var/www/html/fog/service/ipxe
curl -L -o netboot.xyz.kpxe https://boot.netboot.xyz/ipxe/netboot.xyz.kpxe
curl -L -o netboot.xyz.efi  https://boot.netboot.xyz/ipxe/netboot.xyz.efi
ls -lh netboot.xyz.*
```

### 2) Créer 2 entrées FOG iPXE (une BIOS, une UEFI)

FOG Web → **iPXE New Menu Entry**

#### A) Legacy BIOS

Menu Item: **netboot.xyz (BIOS)**

Parameters:

!!! warning "À adapter"
	Remplace **XXX.XXX.XXX.XXX** par l’IP de ton serveur FOG.

chain http://XXX.XXX.XXX.XXX/fog/service/ipxe/netboot.xyz.kpxe

#### B) UEFI

Menu Item: **netboot.xyz (UEFI)**

Parameters:

!!! warning "À adapter"
	Remplace **XXX.XXX.XXX.XXX** par l’IP de ton serveur FOG.

chain http://XXX.XXX.XXX.XXX/fog/service/ipxe/netboot.xyz.efi

Met Menu Show with = **All Hosts** (ou Not Registered Hosts selon ton besoin). **Save.**

🔗 Liens utiles

- 🌐 [Documentation officielle FOG](https://docs.fogproject.org/en/latest/)
- 💻 [Dépôt GitHub du Runbook](https://github.com/MilesChristi/runbook)