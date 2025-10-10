async function post(url, payload={}) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });
  return await res.json().catch(()=>({}));
}

document.addEventListener("click", async (e)=>{
  const like = e.target.closest("[data-like]");
  const connect = e.target.closest("[data-connect]");
  const chat = e.target.closest("[data-chat]");
  const close = e.target.closest("[data-close]");

  if (like){
    const id = like.dataset.like;
    const r = await post(`/like/${id}`);
    like.classList.toggle("active", r.action === "added");
    return;
  }
  if (connect){
    const id = connect.dataset.connect;
    await post(`/connect/${id}`);
    connect.textContent = "Connected ✓";
    connect.classList.add("ok");
    return;
  }
  if (chat){
    const modal = document.getElementById("chat-modal");
    if (modal){ modal.style.display = "block"; }
    return;
  }
  if (close){
    const modal = document.getElementById("chat-modal");
    if (modal){ modal.style.display = "none"; }
    return;
  }
});
