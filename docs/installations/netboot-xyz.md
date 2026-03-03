#Implémentation D'outils et autres sur PXE

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