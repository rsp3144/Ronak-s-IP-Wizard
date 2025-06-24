import streamlit as st
import ipaddress
import pandas as pd

st.set_page_config(page_title="Advanced Subnet Calculator", layout="centered")
st.title("📡 Advanced Subnet Calculator")

# Inputs
base_network = st.text_input("Enter base network (e.g., 101.0.0.0/8)", "101.0.0.0/8")
subnet_prefix = st.number_input("Enter new subnet prefix (CIDR)", min_value=8, max_value=30, value=19)
start_index = st.number_input("Start subnet index", min_value=1, value=1)
count = st.number_input("How many subnets to list?", min_value=1, max_value=2000, value=5)

# 📐 Show calculations before displaying the subnet table
st.subheader("📘 Subnetting Calculations")

try:
    original_prefix = int(base_network.split("/")[1])
    bits_borrowed = subnet_prefix - original_prefix
    total_hosts = 2 ** (32 - subnet_prefix)
    usable_hosts = total_hosts - 2
    mask_ip = ipaddress.IPv4Network(f"0.0.0.0/{subnet_prefix}").netmask.exploded

    # Determine subnet increment
    octets = mask_ip.split(".")
    if subnet_prefix > 24:
        increment = 256 - int(octets[3])
    elif subnet_prefix > 16:
        increment = 256 - int(octets[2])
    elif subnet_prefix > 8:
        increment = 256 - int(octets[1])
    else:
        increment = 256 - int(octets[0])

    # Display calculations
    st.markdown(f"**Bits Borrowed:** {bits_borrowed}")
    st.markdown(f"**New Subnet Mask (/CIDR):** /{subnet_prefix} — {mask_ip}")
    st.markdown(f"**Subnet Increment (per block):** {increment}")
    st.markdown(f"**Usable Hosts per Subnet:** {usable_hosts}")
except Exception as e:
    st.warning(f"Subnetting math skipped: {e}")

# Generate subnets on button click
if st.button("Generate Subnet Table"):
    try:
        base = ipaddress.ip_network(base_network, strict=False)
        subnets = list(base.subnets(new_prefix=subnet_prefix))

        if start_index + count - 1 > len(subnets):
            st.error(f"Only {len(subnets)} subnets available. Adjust your count or starting index.")
        else:
            data = []
            for i in range(start_index - 1, start_index - 1 + count):
                net = subnets[i]
                hosts = list(net.hosts())
                data.append({
                    "Subnet #": i + 1,
                    "Network": str(net.network_address),
                    "Usable Start": str(hosts[0]),
                    "Usable End": str(hosts[-1]),
                    "Broadcast": str(net.broadcast_address),
                    "Usable Hosts": len(hosts)
                })

            df = pd.DataFrame(data)
            st.success(f"Showing subnets {start_index} to {start_index + count - 1}")
            st.dataframe(df)

            # Download option
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv, file_name="subnets.csv", mime="text/csv")

            # Simple visual
            st.subheader("📊 Subnet Range Overview")
            st.bar_chart(df["Usable Hosts"])
    except Exception as e:
        st.error(f"Something went wrong: {e}")
