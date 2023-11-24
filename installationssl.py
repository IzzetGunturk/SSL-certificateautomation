import subprocess

# Path for the script
script_dir = subprocess.run(["dirname", __file__], capture_output=True, text=True).stdout.strip()

# Directory for certificates
certificate_dir = f"{script_dir}/dirCA"

# Separator for output
divider = "\n---------------------------------------------------------------------\n"

# Server IP address
ip = subprocess.run(["hostname", "-I"], capture_output=True, text=True).stdout.strip()

print(divider)

# Ask about installing Apache
webserver_choice = input("Which webserver do you want to install?\n1) Apache\n2) Nothing, Apache is already installed \n\nChoice: ")

while True:
    if webserver_choice in ["1", "2"]:
        if webserver_choice == "1":
            webserver = "Apache"
            webinstall = "apache2"
        else:
            webinstall = "none"
        print(divider)
        break
    else:
        print("Invalid input, the program stops.")
        exit()

if webinstall != "none":
    update_choice = input("Do you want to update the machine before the installation of {}?\n1) Yes\n2) No\n\nChoice: ".format(webserver))

    while True:
        if update_choice in ["1", "2"]:
            update = "yes" if update_choice == "1" else "no"
            print(divider)
            break
        else:
            print("Invalid input, the program stops.")
            exit()

domainname = input("For which domain should the certificate be installed?\nFor example: example.com\nFill in the domain name: ")

while True:
    if any(domainname.endswith(ext) for ext in [".com", ".nl", ".nu", ".local", ".technology", ".localhost", ".lan"]):
        print(divider)
        break
    else:
        print("Invalid input, the program stops.")
        exit()

if webinstall == "none":
    confirm = input("The next steps should be executed:\n\n1) The certificate will be installed for the domain name {} \n\nDo you agree with this? (yes/no) ".format(domainname))
else:
    confirm = input("The next steps should be executed:\n\n1) The machine will be updated\n2) The certificate will be installed for the domain name {} \n\nDo you agree with this? (yes/no) ".format(domainname))

if confirm.lower() in ["yes", "y"]:
    print(divider)
    print("The actions are being performed...")
else:
    print(divider)
    print("The script is aborted.")
    exit()

# Updating the machine (if chosen)
if update == "yes":
    print(divider)
    print("The machine will be updated...")
    subprocess.run(["sudo", "apt-get", "update"])
    subprocess.run(["sudo", "apt-get", "upgrade", "-y"])

# Install Apache (if chosen)
if webinstall != "none":
    print(divider)
    print("The {} webserver will be installed...".format(webserver))
    subprocess.run(["sudo", "apt-get", "install", "-y", webinstall])

# Apache configuration
if webserver == "Apache":
    print(divider)
    print("A CA certificate, private key, and certificate request will be generated...")
    subprocess.run(["sudo", "openssl", "req", "-new", "-x509", "-days", "365", "-extensions", "v3_ca", "-keyout", "{}/myCA.key".format(certificate_dir), "-out", "{}/myCA.crt".format(certificate_dir), "-subj", "/CN={}".format(domainname)])
    subprocess.run(["sudo", "openssl", "genrsa", "-out", "{}/{}.key".format(certificate_dir, domainname), "2048"])
    subprocess.run(["sudo", "openssl", "req", "-new", "-key", "{}/{}.key".format(certificate_dir, domainname), "-out", "{}/{}.csr".format(certificate_dir, domainname), "-subj", "/CN={}".format(domainname)])

    print(divider)
    print("The certificate files will be moved to the right locations...")
    subprocess.run(["sudo", "mkdir", "-p", "/etc/apache2/ssl/{}/".format(domainname)])
    subprocess.run(["sudo", "mv", "{}/{}.key".format(certificate_dir, domainname), "/etc/apache2/ssl/{}/".format(domainname)])
    subprocess.run(["sudo", "mv", "{}/{}.csr".format(certificate_dir, domainname), "/etc/apache2/ssl/{}/".format(domainname)])
    subprocess.run(["sudo", "mv", "{}/myCA.crt".format(certificate_dir), "/etc/apache2/ssl/{}/".format(domainname)])

    print(divider)
    print("The Apache configuration files are being modified...")
    subprocess.run(["sudo", "sed", "-i", "s/#LoadModule ssl_module/LoadModule ssl_module/", "/etc/apache2/mods-available/ssl.conf"])
    subprocess.run(["sudo", "sed", "-i", "s/#SSLCertificateFile/SSLCertificateFile/", "/etc/apache2/mods-available/ssl.conf"])
    subprocess.run(["sudo", "sed", "-i", "s+#SSLCertificateKeyFile+SSLCertificateKeyFile+", "/etc/apache2/mods-available/ssl.conf"])
    subprocess.run(["sudo", "sed", "-i", "s+SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem+SSLCertificateFile /etc/apache2/ssl/{}/{}.crt+".format(domainname, domainname), "/etc/apache2/mods-available/ssl.conf"])
    subprocess.run(["sudo", "sed", "-i", "s+SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key+SSLCertificateKeyFile /etc/apache2/ssl/{}/{}.key+".format(domainname, domainname), "/etc/apache2/mods-available/ssl.conf"])
    subprocess.run(["sudo", "sed", "-i", "s/#SSLProtocol all -SSLv3/SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1/", "/etc/apache2/mods-available/ssl.conf"])
    subprocess.run(["sudo", "a2enmod", "ssl"])
    subprocess.run(["sudo", "systemctl", "restart", "apache2"])

    print(divider)
    print("The certificate is installed on the Apache webserver!")

print(divider)
print("The script has been successfully executed!")
