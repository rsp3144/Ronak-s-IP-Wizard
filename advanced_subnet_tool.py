import streamlit as st
import ipaddress
import pandas as pd

st.set_page_config(page_title="Advanced Subnet Calculator", layout="centered")
st.title("📡 Advanced Subnet Calculator")

# User Inputs
base_network = st.text_input("Enter base network (e.g., 101.0.0.0/8)", "101.0.0.0/8")
subnet_prefix = st.number_input("New Subnet Prefix (CIDR)", min_value=8, max_value=30, value=19)
start_index = st.number_input("Start Subnet Index", min_value=1, value=1)
count = st.number_input("How Many Subnets to List?", min_value=1, max_value=2000, value=5)

# 📘 Subnetting Calculations Section
st.subheader("📘 Subnetting Calculations")

try:
    original_prefix = int(base_network.split("/")[1])
    bits_borrowed = subnet_prefix - original_prefix
    mask_ip = ipaddress.IPv4Network(f"0.0.0.0/{subnet_prefix}").netmask.exploded
    total_hosts = 2 ** (32 - subnet_prefix)
    usable_hosts = total_hosts - 2

    octets = mask_ip.split(".")
    if subnet_prefix > 24:
        increment = 256 - int(octets[3])
        octet_level = "4th"
    elif subnet_prefix > 16:
        increment = 256 - int(octets[2])
        octet_level = "3rd"
    elif subnet_prefix > 8:
        increment = 256 - int(octets[1])
        octet_level = "2nd"
    else:
        increment = 256 - int(octets[0])
        octet_level = "1st"

    st.markdown(f"**Original CIDR Prefix:** /{original_prefix}")
    st.markdown(f"**New Subnet Prefix (CIDR):** /{subnet_prefix}")
    st.markdown(f"**Bits Borrowed:** {bits_borrowed}")
    st.markdown(f"**Subnet Mask:** {mask_ip}")
    st.markdown(f"**Subnet Increment:** {increment} (in the {octet_level} octet)")
    st.markdown(f"**Usable Hosts per Subnet:** {usable_hosts}")

except Exception as e:
    st.warning(f"Subnetting logic skipped: {e}")

# Generate Subnets
if st.button("Generate Subnet Table"):
    try:
        base = ipaddress.ip_network(base_network, strict=False)
        subnets = list(base.subnets(new_prefix=subnet_prefix))

        if start_index + count - 1 > len(subnets):
            st.error(f"Only {len(subnets)} subnets available. Adjust the range.")
        else:
            rows = []
            for i in range(start_index - 1, start_index - 1 + count):
                net = subnets[i]
                hosts = list(net.hosts())
                rows.append({
                    "Subnet #": i + 1,
                    "Network": str(net.network_address),
                    "Usable Start": str(hosts[0]),
                    "Usable End": str(hosts[-1]),
                    "Broadcast": str(net.broadcast_address),
                    "Usable Hosts": len(hosts)
                })

            df = pd.DataFrame(rows)
            st.success(f"Showing subnets {start_index} to {start_index + count - 1}")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv, file_name="subnet_table.csv", mime="text/csv")

            st.subheader("📊 Subnet Host Distribution")
            st.bar_chart(df["Usable Hosts"])

    except Exception as e:
        st.error(f"Something went wrong: {e}")
