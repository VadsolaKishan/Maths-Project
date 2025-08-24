import streamlit as st
import requests, numpy as np, json
from datetime import datetime
import os, uuid

st.set_page_config(page_title="Matrix Calculator", layout="wide")

API_BASE = "https://maths-project-kishan-vadsola.onrender.com"   # 👈 change if deployed online

# --- persistent machine_id ---
MID_FILE = ".machine_id"
if os.path.exists(MID_FILE):
    with open(MID_FILE,"r") as f: machine_id = f.read().strip()
else:
    machine_id = str(uuid.uuid4())
    with open(MID_FILE,"w") as f: f.write(machine_id)

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Calculator","History"])

if page == "Calculator":
    st.title("Matrix Calculator")
    left,right = st.columns([2,1])

    def resize_matrix(mat,r,c):
        if not mat: return [[0]*c for _ in range(r)]
        while len(mat)<r: mat.append([0]*c)
        while len(mat)>r: mat.pop()
        for i in range(r):
            while len(mat[i])<c: mat[i].append(0)
            while len(mat[i])>c: mat[i].pop()
        return mat

    with left:
        rowsA = st.number_input("Rows (A)",1,10,2); colsA = st.number_input("Cols (A)",1,10,2)
        rowsB = st.number_input("Rows (B)",1,10,2); colsB = st.number_input("Cols (B)",1,10,2)
        st.markdown("---")

        if "A" not in st.session_state: st.session_state.A=[[0]*colsA for _ in range(rowsA)]
        st.session_state.A = resize_matrix(st.session_state.A,rowsA,colsA)
        st.write("Matrix A")
        for i in range(rowsA):
            cols = st.columns(colsA)
            for j in range(colsA):
                st.session_state.A[i][j] = int(cols[j].number_input(f"A[{i+1},{j+1}]",value=st.session_state.A[i][j],step=1,key=f"A-{i}-{j}"))

        if "B" not in st.session_state: st.session_state.B=[[0]*colsB for _ in range(rowsB)]
        st.session_state.B = resize_matrix(st.session_state.B,rowsB,colsB)
        st.write("Matrix B")
        for i in range(rowsB):
            cols = st.columns(colsB)
            for j in range(colsB):
                st.session_state.B[i][j] = int(cols[j].number_input(f"B[{i+1},{j+1}]",value=st.session_state.B[i][j],step=1,key=f"B-{i}-{j}"))

        op = st.radio("Operation",("add","sub","mul","transposeA","transposeB"),horizontal=True)

        if st.button("Run"):
            payload={"machine_id":machine_id,"A":st.session_state.A,"B":st.session_state.B,"operation":op}
            try:
                resp=requests.post(f"{API_BASE}/calculate",json=payload,timeout=10)
                data=resp.json()
                if resp.ok:
                    st.session_state.last_result=data["result"]
                    st.success("✅ Saved in history")
                else: st.error(data.get("error","Unknown error"))
            except Exception as e:
                st.error(f"Network/API error: {e}")

    with right:
        st.subheader("Result")
        if "last_result" in st.session_state: st.table(np.array(st.session_state.last_result))
        else: st.write("_No result yet_")

elif page=="History":
    st.header("History")
    limit=st.sidebar.slider("Entries",1,20,5)
    try:
        r=requests.get(f"{API_BASE}/history?limit={limit}&machine_id={machine_id}",timeout=5)
        history=r.json() if r.ok else []
    except Exception as e:
        st.error(f"Fetch failed: {e}"); history=[]

    if history:
        for h in history:
            st.markdown(f"**#{h['id']} — {h['operation']}** _{h['time']}_")
            st.table(np.array(h["A"])); st.table(np.array(h["B"])); st.table(np.array(h["result"]))
    else: st.write("_No history yet_")
