# FOG - Installation

### 🧩 FOG Project
**FOG Project** est une solution open-source de déploiement et de clonage de postes informatiques utilisant le réseau (**PXE**).
Il permet de **capturer**, **stocker** et **déployer des images système** (Windows, Linux, etc.) sur un grand nombre de machines, de manière centralisée et automatisée.

### 🎯 À quoi ça sert ?
- Installer rapidement un système sur plusieurs PC

- Restaurer des postes en cas de panne

- Standardiser les configurations

- Gagner du temps dans les environnements écoles, entreprises ou laboratoires

### ⚙️ Fonctions principales
- Déploiement par PXE (boot réseau)

- Gestion d’images disque

- Inventaire matériel automatique

- Déploiement unicast ou multicast

- Interface web d’administration

### ⚠️ Risques
- Mauvaise configuration DHCP  
- Conflit avec serveur DHCP existant  

### 🖥️ Matériel

- Serveur physique ou machine virtuelle dédiée

- Minimum recommandé :

	- **CPU : 2 cœurs**

	- **RAM : 4 Go (8 Go conseillé)**

	- **Stockage : 100 Go minimum (selon nombre d’images)**

### 🐧 Système d’exploitation supporté

- Debian 12 / 13

- Ubuntu Server 20.04 / 22.04 / 24.04

**Installation minimale** (sans interface graphique recommandée)

### 🌐 Réseau

- Carte réseau configurée en IP fixe

- Accès Internet fonctionnel

- Accès aux ports nécessaires :

	- **UDP 69 (TFTP)**

	- **UDP 4011 (PXE)**

	- **TCP 80 (HTTP)**

	- **TCP 443 (HTTPS)**

### ⚙ Services réseau

Selon ton infrastructure :

- Soit FOG gère le DHCP  
- Soit un serveur DHCP existant + dnsmasq en mode ProxyDHCP  

⚠️ Ne jamais avoir deux serveurs DHCP actifs sur le même réseau.

### 🔐 Accès & droits

- Compte root ou utilisateur avec sudo

- Accès console ou SSH au serveur

### 📦 Paquets requis

- curl

- git

- wget

(installés automatiquement dans la plupart des cas)

### 🧠 BIOS / UEFI des clients

- Boot réseau (PXE) **activé**

- Désactiver **Secure Boot** si nécessaire

- Mode **UEFI** ou **Legacy** connu

### 📄 Informations à préparer

Adresse IP du serveur FOG

Masque réseau

Passerelle

Plage DHCP (si utilisée)

---

### 🧭 Procédure

### 1) Installation du serveur FOG (sans le service DHCP integré)

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install curl -y
sudo apt install git -y
```

Depuis le répertoire personnel de l’utilisateur connecté, exécutez la commande ci-dessous, puis patientez pendant le téléchargement des composants nécessaires.

```bash
git clone https://github.com/fogproject/fogproject.git fogproject-stable
```

Accédez au dossier contenant les scripts d’installation, Le programme d’installation automatisé se nomme **installfog.sh**, exécutez la commande.

```bash
cd fogproject-stable/bin
sudo ./installfog.sh
```

Au lancement de l'installateur FOG, une fenêtre s'affiche :

![[Procédure]](../assets/png.png)

Une fois le processus terminé, se connecter via navigateur à l’adresse indiquée :

http://XXX.XXX.XXX.XXX/fog/management

!!! danger "ATTENTION"
    Ne pas faire "Entrée" tout de suite.  
    Lancer d’abord le navigateur pour initialiser la base de données.
	
L’installation de Fog se termine sur Debian (configuration des derniers paquets et services). On obtient un récapitulatif
complet avec les identifiants par défaut nécessaires à la première connexion à l’interface web de FOG :

!!! note "Identifiants par défaut FOG"
    - **Username :** Fog  
    - **Password :** password

### 2) Installation dnsmasq (ProxyDHCP)

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y dnsmasq
dnsmasq --version
```


### 3) Créer le fichier de configuration dnsmasq

!!! warning "À adapter"
	Remplace 192.168.1.66 par l’IP de ton serveur FOG et ajuste le dhcp-range.

```bash	
# ================================
# DNSMASQ ProxyDHCP pour FOG
# Debian 13
# ================================

# Ne pas faire serveur DNS
port=0

# Logs DHCP
log-dhcp

# Activer / Désactiver TFTP
#enable-tftp
#tftp-root=/tftpboot

# Ne pas écraser options DHCP
dhcp-no-override

# Détection du type de firmware
dhcp-vendorclass=BIOS,PXEClient:Arch:00000
dhcp-vendorclass=UEFI32,PXEClient:Arch:00006
dhcp-vendorclass=UEFI,PXEClient:Arch:00007
dhcp-vendorclass=UEFI64,PXEClient:Arch:00009

# BIOS Legacy
dhcp-boot=undionly.kpxe,,192.168.1.66

# UEFI
dhcp-boot=net:UEFI32,i386-efi/ipxe.efi,,192.168.1.66
dhcp-boot=net:UEFI,ipxe.efi,,192.168.1.66
dhcp-boot=net:UEFI64,ipxe.efi,,192.168.1.66

# Menu PXE
pxe-prompt="Booting FOG Client", 1

pxe-service=X86PC,"Boot to FOG",undionly.kpxe
pxe-service=X86-64_EFI,"Boot to FOG UEFI",ipxe.efi
pxe-service=BC_EFI,"Boot to FOG UEFI PXE-BC",ipxe.efi

# Mode ProxyDHCP
dhcp-range=192.168.1.0,proxy
```

### 4) Redémarrer et activer dnsmasq 

```bash
sudo systemctl restart dnsmasq
sudo systemctl enable dnsmasq
```

### 5) Vérifier que le port 69 (TFTP) écoute

```bash
sudo ss -anu | grep :69
```

```bash
UNCONN 0 0 0.0.0.0:69
```

### 6) Vérifier que FOG fournit bien les fichiers PXE

```bash
ls /tftpboot
```

### 7) Ouvrir les ports pare-feu (si actif)

```bash
sudo apt install -y ufw
sudo ufw allow 69/udp
sudo ufw allow 4011/udp
sudo ufw allow 80
sudo ufw allow 443
sudo ufw reload
```

### 🧪 Vérifications finales

### 1) Utiliser FOG Project

#### A) Préparation de la machine Maitre

Dans cette phase, une machine de référence va être intégrée dans la base d’inventaire de FOG afin de servir de **poste maître** pour la création d’images système.
Cette opération nécessite l’utilisation d’un poste Windows opérationnel. Pour les besoins de ce guide, une machine virtuelle sous **Windows 11** est utilisée comme système modèle.

!!! warning "OS - Windows" 
	Préconisation spécifique aux systèmes Windows

Avant toute interaction avec FOG, certaines fonctionnalités d’économie d’énergie doivent être neutralisées sur le poste modèle.
Les systèmes Windows 10 et 11 activent par défaut l’hibernation, ce qui peut empêcher le bon déroulement des opérations de capture et de déploiement d’images.

**Désactivation de l’hibernation**

Sur la machine Windows :

- Ouvrir une invite de commandes avec des **privilèges administrateur**

- Exécuter la commande suivante :

```bash
powercfg -H off
```

- Confirmer l’exécution de la commande et fermer l’invite de commandes

- Procéder à l’extinction complète du système via le menu de démarrage de Windows

La machine est désormais prête pour être configurée en démarrage réseau (PXE).
Lors du prochain allumage, elle initiera une séquence de boot sur l’interface réseau, établira une communication avec le serveur FOG.

#### B) Mise en place du démarrage PXE sur Machine Hyper-V (Windows 11)

Le poste Windows utilisé étant une **machine virtuelle**, il est nécessaire de configurer son mode de démarrage afin de privilégier l’amorçage réseau (**PXE**).
Cette configuration permet au système de contacter le serveur FOG lors du démarrage et d’être automatiquement enregistré dans l’inventaire.

Pour cela, modifier la **séquence de boot** de la machine virtuelle :

 - Sélectionner la machine virtuelle dans l’interface de gestion

 - Accéder aux paramètres ou options de la machine

 - Ouvrir la section relative à l’**ordre d’amorçage**

 - Positionner l’interface réseau (**Ethernet / Network / PXE**) comme premier périphérique de démarrage

Une fois ce réglage appliqué, la machine tentera en priorité un démarrage sur le réseau lors de sa prochaine mise sous tension.

#### C) Enregistrement de la machine Windows dans l'inventaire FOG

Démarrer la machine Windows.
Si la configuration PXE est correcte, le poste effectue un amorçage réseau, obtient une adresse IP via DHCP et affiche le menu de démarrage FOG.

![[Procédure]](../assets/registration.png)

À l’aide des touches directionnelles, sélectionner l’option :

**Quick Registration and Inventory**

puis valider avec **Entrée**.

Le processus d’enregistrement s’exécute automatiquement et ne nécessite aucune interaction supplémentaire.
Une fois l’opération terminée, arrêter la machine Windows (un redémarrage peut être proposé).

**Vérification de l’enregistrement**

Afin de confirmer que le poste a bien été intégré dans FOG :

 - Accéder à l’interface web FOG

 - Se connecter avec un compte administrateur

 - Depuis le tableau de bord, ouvrir le menu **Hosts**

 - Cliquer sur **List All Hosts**

Le poste Windows doit apparaître dans la liste des hôtes, confirmant son ajout à l’inventaire.

![[Procédure]](../assets/registration00.png)

Une fois le poste présent dans l’inventaire, il est recommandé de lui attribuer un nom explicite afin de faciliter son identification.

 - Cliquer sur le nom actuel de la machine (affiché en bleu)

 - Renseigner un nom représentatif, par exemple : **Win11_modele**

 - Enregistrer la modification

Afin d’améliorer l’organisation de l’inventaire, le poste peut ensuite être rattaché à un groupe d’hôtes.

Pour créer et associer un groupe :

 - Saisir le nom du groupe souhaité dans le champ **Create new group**

 - Cliquer sur le bouton **Update** afin de valider
 
![[Procédure]](../assets/registration01.png)

La machine est désormais correctement nommée et intégrée dans une structure hiérarchique facilitant la gestion des postes.

Pour associer le poste au groupe précédemment créé :

- Revenir dans le menu **Hosts** puis cliquer sur **List All Hosts**

- Cocher la case située à gauche de la machine concernée

- Dans la section **Add to group**, sélectionner le groupe souhaité

- Cliquer sur le bouton **Update** afin d’appliquer la modification

![[Procédure]](../assets/registration02.png)

La machine est désormais rattachée au groupe défini.

#### D) Création d'une tâche pour la capture de la machine

Avant toute opération de déploiement, il est nécessaire de **créer une image système** à partir d’un poste de référence.
Une fois la machine Windows enregistrée dans l’inventaire FOG lors de son premier démarrage, il convient de lui attribuer une **tâche de capture**.
Cette action déclenche, lors du prochain démarrage du poste modèle, la création d’une image disque qui pourra ensuite être utilisée pour des déploiements automatisés.

**Création de l’image**

Depuis le menu principal de l’interface FOG, ouvrir la section **Images**

Cliquer sur **Create New Image**

Renseigner les différents champs requis

Valider en cliquant sur **Add**

![[Procédure]](../assets/capture00.png)

#### E) Mise en place de la tâche capture

Afin que le poste Windows utilisé comme système de référence soit automatiquement capturé lors de son prochain démarrage, il est nécessaire de planifier une tâche de capture depuis l’interface FOG.

Procédure :

- Ouvrir le menu **Hosts** dans l’interface FOG

- Cliquer sur **List All Hosts** afin d’afficher l’inventaire

- Cocher la case correspondant à la machine modèle

- Cliquer sur l’icône **Goto Task List** (icône bleue en forme de croix)

- Dans la fenêtre qui s’ouvre, sélectionner l’option **Capture**

- Valider en cliquant sur le bouton **Task**

Un message de confirmation indique que la tâche a bien été créée.

Pour vérifier :

- Accéder au menu **Tasks**

- Contrôler que la tâche de capture est bien associée à la machine modèle

La machine est désormais prête pour le lancement de la capture automatisée de son système.

À l’issue de la capture, procéder à l’arrêt complet de la machine Windows ayant servi de poste modèle, puis revenir sur l’interface d’administration du serveur FOG.

- Ouvrir le menu **Images**

- Cliquer sur **List All Images**

L’image nouvellement créée doit apparaître dans la liste, confirmant que la capture s’est déroulée correctement.
Dans cet exemple, l’image du poste Windows 11 modèle occupe environ 10,5 Go après compression au format **ZST**.

#### F) Déploiement d'une nouvelle machine

La phase suivante consiste à **valider l’image capturée** en effectuant un déploiement sur un poste vierge.
Pour ce test, une nouvelle machine Windows sans système installé est créée, puis un déploiement manuel est lancé depuis le serveur FOG.
À noter qu’il est également possible d’automatiser les déploiements et d’utiliser le mode **multicast** pour déployer simultanément plusieurs postes.

Sur l’hyperviseur Proxmox, créer une **nouvelle machine virtuelle vierge** en définissant uniquement les ressources nécessaires au fonctionnement du futur système (par exemple : 8 Go de mémoire, un disque de 50 Go).
Configurer la machine pour un **démarrage réseau PXE** et ne pas attacher de fichier ISO.

Vérifier que la machine virtuelle est connectée au réseau local interne (LAN).
Dans les paramètres réseau, sélectionner l’interface correspondant au réseau de production.

Démarrer la machine afin qu’elle effectue un boot PXE, puis attendre l’affichage du menu FOG.

Sélectionner l’option **Deploy Image**

Lors de l’invite d’authentification, renseigner les identifiants du serveur FOG :

**Username** : fog

**Password** : password

!!! danger "ATTENTION"
    Le mot de passe doit être saisi en disposition clavier QWERTY (soit **pqsszord**).

Depuis l’interface de démarrage FOG, choisir l’image à déployer à l’aide des flèches directionnelles, puis appuyer sur Entrée afin de lancer le déploiement.

![[Procédure]](../assets/deploi00.png)

#### G) Multicast

en cours ...

TEST01




🔗 Liens utiles

- 🌐 [Documentation officielle FOG](https://docs.fogproject.org/en/latest/)
- 💻 [Dépôt GitHub du Runbook](https://github.com/MilesChristi/runbook)

