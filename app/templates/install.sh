#!/usr/bin/env bash
echo "VM name: {{ vmname }} {{ MSVM_URL }}"

echo "PING INSTALL"
cat > /opt/ms.vm.ping.sh <<'_EOF'
#!/usr/bin/env bash
data=`curl {{ MSVM_URL }}/ping/$("hostname")`
is_exec=`echo '${data}' | python -m json.tool | grep "exec" | wc -l`
if [[ "$is_exec" == "0" ]]; then
    exec_url=`echo '${data}' | python -m json.tool | grep "exec" | wc -l`
    echo "EXEC FOUND: ${exec_url}"
fi
_EOF
chmod +x /opt/ms.vm.ping.sh

echo "CRON INSTALL"
cat > /etc/cron.d/ms_vm_ping <<'_EOF'
* * * * * /opt/ms.vm.ping.sh >> /var/log/ms.vm.log

_EOF

crontab /etc/cron.d/ms_vm_ping

