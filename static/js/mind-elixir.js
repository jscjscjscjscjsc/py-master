const es = 0, ts = 1, ns = 2, fe = {
  name: "Latte",
  type: "light",
  palette: ["#dd7878", "#ea76cb", "#8839ef", "#e64553", "#fe640b", "#df8e1d", "#40a02b", "#209fb5", "#1e66f5", "#7287fd"],
  cssVar: {
    "--node-gap-x": "30px",
    "--node-gap-y": "10px",
    "--main-gap-x": "65px",
    "--main-gap-y": "45px",
    "--root-radius": "30px",
    "--main-radius": "20px",
    "--root-color": "#ffffff",
    "--root-bgcolor": "#4c4f69",
    "--root-border-color": "rgba(0, 0, 0, 0)",
    "--main-border": "",
    // you can customize, it will fallback to 2px solid main-color
    "--main-color": "#444446",
    "--main-bgcolor": "#ffffff",
    "--main-bgcolor-transparent": "rgba(255, 255, 255, 0.8)",
    "--topic-padding": "3px",
    "--color": "#777777",
    "--bgcolor": "#f6f6f6",
    "--selected": "#4dc4ff",
    "--accent-color": "#e64553",
    "--panel-color": "#444446",
    "--panel-bgcolor": "#ffffff",
    "--panel-border-color": "#eaeaea",
    "--map-padding": "50px 80px"
  }
}, ue = {
  name: "Dark",
  type: "dark",
  palette: ["#848FA0", "#748BE9", "#D2F9FE", "#4145A5", "#789AFA", "#706CF4", "#EF987F", "#775DD5", "#FCEECF", "#DA7FBC"],
  cssVar: {
    "--node-gap-x": "30px",
    "--node-gap-y": "10px",
    "--main-gap-x": "65px",
    "--main-gap-y": "45px",
    "--root-radius": "30px",
    "--main-radius": "20px",
    "--root-color": "#ffffff",
    "--root-bgcolor": "#2d3748",
    "--root-border-color": "rgba(255, 255, 255, 0.1)",
    "--main-border": "",
    "--main-color": "#ffffff",
    "--main-bgcolor": "#4c4f69",
    "--main-bgcolor-transparent": "rgba(76, 79, 105, 0.8)",
    "--topic-padding": "3px",
    "--color": "#cccccc",
    "--bgcolor": "#252526",
    "--selected": "#4dc4ff",
    "--accent-color": "#789AFA",
    "--panel-color": "#ffffff",
    "--panel-bgcolor": "#2d3748",
    "--panel-border-color": "#696969",
    "--map-padding": "50px 80px"
  }
};
function ae(e) {
  return e.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
}
const ne = function(e, t) {
  if (t.id === e)
    return t;
  if (t.children && t.children.length) {
    for (let n = 0; n < t.children.length; n++) {
      const o = ne(e, t.children[n]);
      if (o) return o;
    }
    return null;
  } else
    return null;
}, R = (e, t) => {
  if (e.parent = t, e.children)
    for (let n = 0; n < e.children.length; n++)
      R(e.children[n], e);
}, F = (e, t, n) => {
  if (e.expanded = t, e.children)
    if (n === void 0 || n > 0) {
      const o = n !== void 0 ? n - 1 : void 0;
      e.children.forEach((s) => {
        F(s, t, o);
      });
    } else
      e.children.forEach((o) => {
        F(o, !1);
      });
};
function pe(e) {
  if (e.id = B(), e.children)
    for (let t = 0; t < e.children.length; t++)
      pe(e.children[t]);
}
function oe(e, t, n, o) {
  const s = n - e, i = o - t, c = Math.atan2(i, s) * 180 / Math.PI, r = 12, a = 30, d = (c + 180 - a) * Math.PI / 180, h = (c + 180 + a) * Math.PI / 180;
  return {
    x1: n + Math.cos(d) * r,
    y1: o + Math.sin(d) * r,
    x2: n + Math.cos(h) * r,
    y2: o + Math.sin(h) * r
  };
}
function B() {
  return ((/* @__PURE__ */ new Date()).getTime().toString(16) + Math.random().toString(16).substring(2)).substring(2, 18);
}
const mt = function() {
  const e = B();
  return {
    topic: this.newTopicName,
    id: e
  };
};
function ge(e) {
  return JSON.parse(
    JSON.stringify(e, (n, o) => {
      if (n !== "parent")
        return o;
    })
  );
}
const M = (e, t) => {
  let n = 0, o = 0;
  for (; t && t !== e; )
    n += t.offsetLeft, o += t.offsetTop, t = t.offsetParent;
  return { offsetLeft: n, offsetTop: o };
}, k = (e, t) => {
  for (const n in t)
    e.setAttribute(n, t[n]);
}, te = (e) => e ? e.tagName === "ME-TPC" : !1, me = (e) => e.filter((t) => t.nodeObj.parent).filter((t, n, o) => {
  for (let s = 0; s < o.length; s++) {
    if (t === o[s]) continue;
    const { parent: i } = t.nodeObj;
    if (i === o[s].nodeObj)
      return !1;
  }
  return !0;
}), ye = (e) => {
  const t = /translate3d\(([^,]+),\s*([^,]+)/, n = e.match(t);
  return n ? { x: parseFloat(n[1]), y: parseFloat(n[2]) } : { x: 0, y: 0 };
}, qe = function(e) {
  for (let t = 0; t < e.length; t++) {
    const { dom: n, evt: o, func: s } = e[t];
    n.addEventListener(o, s);
  }
  return function() {
    for (let n = 0; n < e.length; n++) {
      const { dom: o, evt: s, func: i } = e[n];
      o.removeEventListener(s, i);
    }
  };
}, De = (e, t) => {
  const n = e.x - t.x, o = e.y - t.y;
  return Math.sqrt(n * n + o * o);
}, yt = function(e, t) {
  if (!t)
    return ie(e), e;
  let n = e.querySelector(".insert-preview");
  const o = `insert-preview ${t} show`;
  return n || (n = document.createElement("div"), e.appendChild(n)), n.className = o, e;
}, ie = function(e) {
  if (!e) return;
  const t = e.querySelectorAll(".insert-preview");
  for (const n of t || [])
    n.remove();
}, Le = function(e, t) {
  for (const n of t) {
    const o = n.parentElement.parentElement.contains(e);
    if (!(e && e.tagName === "ME-TPC" && e !== n && !o && e.nodeObj.parent)) return !1;
  }
  return !0;
}, bt = function(e) {
  const t = document.createElement("div");
  return t.className = "mind-elixir-ghost", e.container.appendChild(t), t;
};
class vt {
  mind;
  isMoving = !1;
  interval = null;
  speed = 20;
  constructor(t) {
    this.mind = t;
  }
  move(t, n) {
    this.isMoving || (this.isMoving = !0, this.interval = setInterval(() => {
      this.mind.move(t * this.speed * this.mind.scaleVal, n * this.speed * this.mind.scaleVal);
    }, 100));
  }
  stop() {
    this.isMoving = !1, this.interval && (clearInterval(this.interval), this.interval = null);
  }
}
function wt(e) {
  return {
    isDragging: !1,
    insertType: null,
    meet: null,
    ghost: bt(e),
    edgeMoveController: new vt(e),
    startX: 0,
    startY: 0,
    pointerId: null
  };
}
const xt = 5;
function Me(e, t, n, o = !1) {
  if (e.spacePressed) return !1;
  const s = n.target;
  if (s?.tagName !== "ME-TPC" || !s.nodeObj.parent) return !1;
  if (t.startX = n.clientX, t.startY = n.clientY, t.pointerId = n.pointerId, e.dragged = e.currentNodes, o) {
    Je(e, t);
    const i = e.container.getBoundingClientRect();
    Ue(t.ghost, n.clientX - i.x, n.clientY - i.y);
  }
  return !0;
}
function Ue(e, t, n) {
  e.style.transform = `translate(${t - 10}px, ${n - 10}px)`, e.style.display = "block";
}
function Je(e, t) {
  const { dragged: n } = e;
  if (!n) return;
  const o = document.activeElement;
  o && o.isContentEditable && o.blur(), t.isDragging = !0, n.length > 1 ? t.ghost.innerHTML = n.length + "" : t.ghost.innerHTML = n[0].innerHTML;
  for (const s of n)
    s.parentElement.parentElement.style.opacity = "0.5";
  e.panHelper.clear();
}
function Et(e, t, n) {
  const { dragged: o } = e;
  if (!o || t.pointerId !== n.pointerId) return;
  const s = n.clientX - t.startX, i = n.clientY - t.startY, l = Math.sqrt(s * s + i * i);
  if (!t.isDragging && l > xt && Je(e, t), !t.isDragging) return;
  const c = e.container.getBoundingClientRect();
  Ue(t.ghost, n.clientX - c.x, n.clientY - c.y), n.clientX < c.x + 50 ? t.edgeMoveController.move(1, 0) : n.clientX > c.x + c.width - 50 ? t.edgeMoveController.move(-1, 0) : n.clientY < c.y + 50 ? t.edgeMoveController.move(0, 1) : n.clientY > c.y + c.height - 50 ? t.edgeMoveController.move(0, -1) : t.edgeMoveController.stop(), ie(t.meet);
  const r = 12 * e.scaleVal, a = document.elementFromPoint(n.clientX, n.clientY - r);
  if (Le(a, o)) {
    t.meet = a;
    const d = a.getBoundingClientRect(), h = d.y;
    n.clientY > h + d.height ? t.insertType = "after" : t.insertType = "in";
  } else {
    const d = document.elementFromPoint(n.clientX, n.clientY + r);
    if (Le(d, o)) {
      t.meet = d;
      const u = d.getBoundingClientRect().y;
      n.clientY < u ? t.insertType = "before" : t.insertType = "in";
    } else
      t.insertType = null, t.meet = null;
  }
  t.meet && yt(t.meet, t.insertType);
}
function Ct(e, t, n) {
  const { dragged: o } = e;
  if (!(!o || t.pointerId !== n.pointerId)) {
    t.edgeMoveController.stop();
    for (const s of o)
      s.parentElement.parentElement.style.opacity = "1";
    t.ghost.style.display = "none", t.ghost.innerHTML = "", t.isDragging && t.meet && (ie(t.meet), t.insertType === "before" ? e.moveNodeBefore(o, t.meet) : t.insertType === "after" ? e.moveNodeAfter(o, t.meet) : t.insertType === "in" && e.moveNodeIn(o, t.meet)), e.dragged = null, t.isDragging = !1, t.insertType = null, t.meet = null, t.pointerId = null;
  }
}
function Ae(e, t) {
  const { dragged: n } = e;
  if (n) {
    t.edgeMoveController.stop();
    for (const o of n)
      o.parentElement.parentElement.style.opacity = "1";
    t.meet && ie(t.meet), t.ghost.style.display = "none", t.ghost.innerHTML = "", e.dragged = null, t.isDragging = !1, t.insertType = null, t.meet = null, t.pointerId = null;
  }
}
function St(e) {
  return () => {
  };
}
const H = {
  LHS: "lhs",
  RHS: "rhs"
}, Nt = function() {
  this.nodes.innerHTML = "";
  const e = this.createTopic(this.nodeData);
  be.call(this, e, this.nodeData), e.draggable = !1;
  const t = document.createElement("me-root");
  t.appendChild(e);
  const n = this.nodeData.children || [];
  if (this.direction === 2) {
    let o = 0, s = 0;
    n.map((i) => {
      i.direction === 0 ? o += 1 : i.direction === 1 ? s += 1 : o <= s ? (i.direction = 0, o += 1) : (i.direction = 1, s += 1);
    });
  }
  Tt(this, n, t);
}, Tt = function(e, t, n) {
  const o = document.createElement("me-main");
  o.className = H.LHS;
  const s = document.createElement("me-main");
  s.className = H.RHS;
  for (let i = 0; i < t.length; i++) {
    const l = t[i], { grp: c } = e.createWrapper(l);
    e.direction === 2 ? l.direction === 0 ? o.appendChild(c) : s.appendChild(c) : e.direction === 0 ? o.appendChild(c) : s.appendChild(c);
  }
  e.nodes.appendChild(o), e.nodes.appendChild(n), e.nodes.appendChild(s), e.nodes.appendChild(e.lines), e.nodes.appendChild(e.labelContainer);
}, kt = function(e, t) {
  const n = document.createElement("me-children");
  for (let o = 0; o < t.length; o++) {
    const s = t[o], { grp: i } = e.createWrapper(s);
    n.appendChild(i);
  }
  return n;
}, Ze = function(e, t) {
  const o = (this?.el ? this.el : t || document).querySelector(`[data-nodeid="me${e}"]`);
  if (!o) throw new Error(`FindEle: Node ${e} not found, maybe it's collapsed.`);
  return o;
}, be = function(e, t) {
  if (e.innerHTML = "", t.style) {
    const n = t.style;
    for (const o in n)
      e.style[o] = n[o];
  }
  if (t.dangerouslySetInnerHTML) {
    e.innerHTML = t.dangerouslySetInnerHTML;
    return;
  }
  if (t.image) {
    const n = t.image;
    if (n.url && n.width && n.height) {
      const o = document.createElement("img");
      o.src = this.imageProxy ? this.imageProxy(n.url) : n.url, o.style.width = n.width + "px", o.style.height = n.height + "px", n.fit && (o.style.objectFit = n.fit), e.appendChild(o), e.image = o;
    }
  } else e.image && (e.image = void 0);
  {
    const n = document.createElement("span");
    n.className = "text", this.markdown ? n.innerHTML = this.markdown(t.topic, t) : n.textContent = t.topic, e.appendChild(n), e.text = n;
  }
  if (t.hyperLink) {
    const n = document.createElement("a");
    n.className = "hyper-link", n.target = "_blank", n.innerText = "🔗", n.href = t.hyperLink, e.appendChild(n), e.link = n;
  } else e.link && (e.link = void 0);
  if (t.icons && t.icons.length) {
    const n = document.createElement("span");
    n.className = "icons", n.innerHTML = t.icons.map((o) => `<span>${ae(o)}</span>`).join(""), e.appendChild(n), e.icons = n;
  } else e.icons && (e.icons = void 0);
  if (t.tags && t.tags.length) {
    const n = document.createElement("div");
    n.className = "tags", t.tags.forEach((o) => {
      const s = document.createElement("span");
      typeof o == "string" ? s.textContent = o : (s.textContent = o.text, o.className && (s.className = o.className), o.style && Object.assign(s.style, o.style)), n.appendChild(s);
    }), e.appendChild(n), e.tags = n;
  } else e.tags && (e.tags = void 0);
}, _t = function(e, t) {
  const n = document.createElement("me-wrapper"), { p: o, tpc: s } = this.createParent(e);
  if (n.appendChild(o), !t && e.children && e.children.length > 0) {
    const i = ve(e.expanded);
    if (o.appendChild(i), e.expanded !== !1) {
      const l = kt(this, e.children);
      n.appendChild(l);
    }
  }
  return { grp: n, top: o, tpc: s };
}, Dt = function(e) {
  const t = document.createElement("me-parent"), n = this.createTopic(e);
  return be.call(this, n, e), t.appendChild(n), { p: t, tpc: n };
}, Lt = function(e) {
  const t = document.createElement("me-children");
  return t.append(...e), t;
}, Mt = function(e) {
  const t = document.createElement("me-tpc");
  return t.nodeObj = e, t.dataset.nodeid = "me" + e.id, t;
};
function Qe(e) {
  const t = document.createRange();
  t.selectNodeContents(e);
  const n = window.getSelection();
  n && (n.removeAllRanges(), n.addRange(t));
}
const At = function(e) {
  if (!e) return;
  const t = document.createElement("div"), n = e.nodeObj, o = n.topic, { offsetLeft: s, offsetTop: i } = M(this.nodes, e);
  this.nodes.appendChild(t), t.id = "input-box", t.textContent = o, t.contentEditable = "plaintext-only", t.spellcheck = !1;
  const l = getComputedStyle(e);
  t.style.cssText = `
  left: ${s}px;
  top: ${i}px;
  min-width:${e.offsetWidth - 8}px;
  color:${l.color};
  font-size:${l.fontSize};
  padding:${l.padding};
  margin:${l.margin}; 
  background-color:${l.backgroundColor !== "rgba(0, 0, 0, 0)" && l.backgroundColor};
  border: ${l.border};
  border-radius:${l.borderRadius}; `, this.direction === 0 && (t.style.right = "0"), e.style.opacity = "0", Qe(t), this.bus.fire("operation", {
    name: "beginEdit",
    obj: e.nodeObj
  }), t.addEventListener("keydown", (c) => {
    c.stopPropagation();
    const r = c.key;
    if (r === "Enter" || r === "Tab") {
      if (c.shiftKey) return;
      c.preventDefault(), t.blur(), this.container.focus();
    } else r === "Escape" && (c.preventDefault(), t.textContent = o, t.blur(), this.container.focus());
  }), t.addEventListener("blur", () => {
    if (!t) return;
    e.style.opacity = "1", t.remove();
    const c = t.innerText?.trim() || "";
    c === o || c === "" || (n.topic = c, this.markdown ? e.text.innerHTML = this.markdown(n.topic, n) : e.text.textContent = c, this.linkDiv(), this.bus.fire("operation", {
      name: "finishEdit",
      obj: n,
      origin: o
    }));
  });
}, ve = function(e) {
  const t = document.createElement("me-epd");
  return t.expanded = e !== !1, t.className = e !== !1 ? "minus" : "", t;
}, K = (e) => {
  const t = e.parent?.children, n = t?.indexOf(e) ?? 0;
  return { siblings: t, index: n };
};
function Pt(e) {
  const { siblings: t, index: n } = K(e);
  if (t === void 0) return;
  const o = t[n];
  n === 0 ? (t[n] = t[t.length - 1], t[t.length - 1] = o) : (t[n] = t[n - 1], t[n - 1] = o);
}
function Ot(e) {
  const { siblings: t, index: n } = K(e);
  if (t === void 0) return;
  const o = t[n];
  n === t.length - 1 ? (t[n] = t[0], t[0] = o) : (t[n] = t[n + 1], t[n + 1] = o);
}
function et(e) {
  const { siblings: t, index: n } = K(e);
  return t === void 0 ? 0 : (t.splice(n, 1), t.length);
}
function Ht(e, t, n) {
  const { siblings: o, index: s } = K(n);
  o !== void 0 && (t === "before" ? o.splice(s, 0, e) : o.splice(s + 1, 0, e));
}
function $t(e, t) {
  const { siblings: n, index: o } = K(e);
  n !== void 0 && (n[o] = t, t.children = [e]);
}
function jt(e, t, n) {
  if (et(t), n.parent?.parent || (t.direction = n.direction), e === "in")
    n.children ? n.children.push(t) : n.children = [t];
  else {
    t.direction !== void 0 && (t.direction = n.direction);
    const { siblings: o, index: s } = K(n);
    if (o === void 0) return;
    e === "before" ? o.splice(s, 0, t) : o.splice(s + 1, 0, t);
  }
}
const It = function({ map: e, direction: t }, n) {
  if (t === 0)
    return 0;
  if (t === 1)
    return 1;
  if (t === 2) {
    const o = e.querySelector(".lhs")?.childElementCount || 0, s = e.querySelector(".rhs")?.childElementCount || 0;
    return o <= s ? (n.direction = 0, 0) : (n.direction = 1, 1);
  }
}, tt = function(e, t, n) {
  const o = n.children[0].children[0], s = t.parentElement;
  if (s.tagName === "ME-PARENT") {
    if (G(o), s.children[1])
      s.nextSibling.appendChild(n);
    else {
      const i = e.createChildren([n]);
      s.appendChild(ve(!0)), s.insertAdjacentElement("afterend", i);
    }
    e.linkDiv(n.offsetParent);
  } else s.tagName === "ME-ROOT" && (It(e, o.nodeObj) === 0 ? e.container.querySelector(".lhs")?.appendChild(n) : e.container.querySelector(".rhs")?.appendChild(n), e.linkDiv());
}, Rt = function(e, t) {
  const n = e.parentNode;
  if (t === 0) {
    const o = n.parentNode.parentNode;
    o.tagName !== "ME-MAIN" && (o.previousSibling.children[1].remove(), o.remove());
  }
  n.parentNode.remove();
}, nt = {
  before: "beforebegin",
  after: "afterend"
}, G = function(e) {
  const n = e.parentElement.parentElement.lastElementChild;
  n?.tagName === "svg" && n?.remove();
}, Bt = function(e, t) {
  const n = e.nodeObj, o = ge(n);
  o.style && t.style && (t.style = Object.assign(o.style, t.style));
  const s = Object.assign(n, t);
  be.call(this, e, s), this.linkDiv(), this.bus.fire("operation", {
    name: "reshapeNode",
    obj: s,
    origin: o
  });
}, we = function(e, t, n) {
  if (!t) return null;
  const o = t.nodeObj;
  o.expanded === !1 && (e.expandNode(t, !0), t = e.findEle(o.id));
  const s = n || e.generateNewObj();
  o.children ? o.children.push(s) : o.children = [s], R(e.nodeData);
  const { grp: i, top: l } = e.createWrapper(s);
  return tt(e, t, i), { newTop: l, newNodeObj: s };
}, Wt = function(e, t, n) {
  const o = t || this.currentNode;
  if (!o) return;
  const s = o.nodeObj;
  if (s.parent) {
    if (!s.parent?.parent && this.direction === 2) {
      const a = this.map.querySelector(".lhs")?.childElementCount || 0, d = this.map.querySelector(".rhs")?.childElementCount || 0;
      if (!a || !d) {
        this.addChild(this.findEle(s.parent.id), n);
        return;
      }
    }
  } else {
    this.addChild();
    return;
  }
  const i = n || this.generateNewObj();
  if (!s.parent?.parent) {
    const a = o.closest("me-main").className === H.LHS ? 0 : 1;
    i.direction = a;
  }
  Ht(i, e, s), R(this.nodeData);
  const l = o.parentElement, { grp: c, top: r } = this.createWrapper(i);
  l.parentElement.insertAdjacentElement(nt[e], c), this.linkDiv(c.offsetParent), n || this.editTopic(r.firstChild), this.bus.fire("operation", {
    name: "insertSibling",
    type: e,
    obj: i
  }), this.selectNode(r.firstChild, !0);
}, Yt = function(e, t) {
  const n = e || this.currentNode;
  if (!n) return;
  G(n);
  const o = n.nodeObj;
  if (!o.parent)
    return;
  const s = t || this.generateNewObj();
  $t(o, s), R(this.nodeData);
  const i = n.parentElement.parentElement, { grp: l, top: c } = this.createWrapper(s, !0);
  c.appendChild(ve(!0)), i.insertAdjacentElement("afterend", l);
  const r = this.createChildren([i]);
  c.insertAdjacentElement("afterend", r), this.linkDiv(), t || this.editTopic(c.firstChild), this.selectNode(c.firstChild, !0), this.bus.fire("operation", {
    name: "insertParent",
    obj: s
  });
}, Xt = function(e, t) {
  const n = e || this.currentNode;
  if (!n) return;
  const o = we(this, n, t);
  if (!o) return;
  const { newTop: s, newNodeObj: i } = o;
  this.bus.fire("operation", {
    name: "addChild",
    obj: i
  }), t || this.editTopic(s.firstChild), this.selectNode(s.firstChild, !0);
}, Ft = function(e, t) {
  const n = ge(e.nodeObj);
  pe(n);
  const o = we(this, t, n);
  if (!o) return;
  const { newNodeObj: s } = o;
  this.selectNode(this.findEle(s.id)), this.bus.fire("operation", {
    name: "copyNode",
    obj: s
  });
}, Kt = function(e, t) {
  const n = [];
  for (let o = 0; o < e.length; o++) {
    const s = e[o], i = ge(s.nodeObj);
    pe(i);
    const l = we(this, t, i);
    if (!l) return;
    const { newNodeObj: c } = l;
    n.push(c);
  }
  this.unselectNodes(this.currentNodes), this.selectNodes(n.map((o) => this.findEle(o.id))), this.bus.fire("operation", {
    name: "copyNodes",
    objs: n
  });
}, Vt = function(e) {
  const t = e || this.currentNode;
  if (!t) return;
  const n = t.nodeObj;
  Pt(n);
  const o = t.parentNode.parentNode;
  o.parentNode.insertBefore(o, o.previousSibling), this.linkDiv(), this.bus.fire("operation", {
    name: "moveUpNode",
    obj: n
  });
}, zt = function(e) {
  const t = e || this.currentNode;
  if (!t) return;
  const n = t.nodeObj;
  Ot(n);
  const o = t.parentNode.parentNode;
  o.nextSibling ? o.nextSibling.insertAdjacentElement("afterend", o) : o.parentNode.prepend(o), this.linkDiv(), this.bus.fire("operation", {
    name: "moveDownNode",
    obj: n
  });
}, Gt = function(e) {
  if (e = me(e), e.length === 0) return;
  for (const n of e) {
    const o = n.nodeObj, s = et(o);
    Rt(n, s);
  }
  const t = e[e.length - 1];
  this.selectNode(this.findEle(t.nodeObj.parent.id)), this.linkDiv(), this.bus.fire("operation", {
    name: "removeNodes",
    objs: e.map((n) => n.nodeObj)
  });
}, xe = (e, t, n, o) => {
  e = me(e);
  let s = n.nodeObj;
  t === "in" && s.expanded === !1 && (o.expandNode(n, !0), n = o.findEle(s.id), s = n.nodeObj), t === "after" && (e = e.reverse());
  const i = [];
  for (const c of e) {
    const r = c.nodeObj;
    if (jt(t, r, s), R(o.nodeData), t === "in") {
      const a = c.parentElement;
      tt(o, n, a.parentElement);
    } else {
      G(c);
      const a = c.parentElement.parentNode;
      i.includes(a.parentElement) || i.push(a.parentElement), n.parentElement.parentNode.insertAdjacentElement(nt[t], a);
    }
  }
  for (const c of i)
    c.childElementCount === 0 && c.tagName !== "ME-MAIN" && (c.previousSibling.children[1].remove(), c.remove());
  o.linkDiv(), o.scrollIntoView(e[e.length - 1]);
  const l = t === "before" ? "moveNodeBefore" : t === "after" ? "moveNodeAfter" : "moveNodeIn";
  o.bus.fire("operation", {
    name: l,
    objs: e.map((c) => c.nodeObj),
    toObj: s
  });
}, qt = function(e, t) {
  xe(e, "in", t, this);
}, Ut = function(e, t) {
  xe(e, "before", t, this);
}, Jt = function(e, t) {
  xe(e, "after", t, this);
}, Zt = function(e) {
  const t = e || this.currentNode;
  t && (t.nodeObj.dangerouslySetInnerHTML || this.editTopic(t));
}, Qt = function(e, t) {
  e.text.textContent = t, e.nodeObj.topic = t, this.linkDiv();
}, ot = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  addChild: Xt,
  beginEdit: Zt,
  copyNode: Ft,
  copyNodes: Kt,
  insertParent: Yt,
  insertSibling: Wt,
  moveDownNode: zt,
  moveNodeAfter: Jt,
  moveNodeBefore: Ut,
  moveNodeIn: qt,
  moveUpNode: Vt,
  removeNodes: Gt,
  reshapeNode: Bt,
  rmSubline: G,
  setNodeTopic: Qt
}, Symbol.toStringTag, { value: "Module" }));
function en(e) {
  return {
    nodeData: e.isFocusMode ? e.nodeDataBackup : e.nodeData,
    arrows: e.arrows,
    summaries: e.summaries,
    direction: e.direction,
    theme: e.theme,
    compact: e.compact,
    meta: e.meta
  };
}
const tn = function(e, t = !1) {
  const n = this.container, o = e.getBoundingClientRect(), s = n.getBoundingClientRect();
  if (t || o.top > s.bottom - 50 || o.bottom < s.top + 50 || o.left > s.right - 50 || o.right < s.left + 50) {
    const l = o.left + o.width / 2, c = o.top + o.height / 2, r = s.left + s.width / 2, a = s.top + s.height / 2, d = l - r, h = c - a;
    this.move(-d, -h, !0);
  }
}, nn = function(e, t, n) {
  this.clearSelection(), this.scrollIntoView(e), this.selection?.select(e), t && this.bus.fire("selectNewNode", e.nodeObj);
}, on = function(e) {
  this.selection?.select(e);
}, sn = function(e) {
  this.selection?.deselect(e);
}, rn = function() {
  this.unselectNodes(this.currentNodes), this.unselectSummary(), this.unselectArrow();
}, Ee = function(e) {
  return JSON.stringify(e, (t, n) => {
    if (!(t === "parent" && typeof n != "string"))
      return n;
  });
}, ln = function() {
  const e = en(this);
  return Ee(e);
}, cn = function() {
  return JSON.parse(this.getDataString());
}, an = function() {
  this.editable = !0;
}, dn = function() {
  this.editable = !1;
}, hn = function(e, t = { x: 0, y: 0 }) {
  if (e < this.scaleMin && e < this.scaleVal || e > this.scaleMax && e > this.scaleVal) return;
  const n = this.container.getBoundingClientRect(), o = t.x ? t.x - n.left - n.width / 2 : 0, s = t.y ? t.y - n.top - n.height / 2 : 0, { dx: i, dy: l } = Ce(this), c = this.map.style.transform, { x: r, y: a } = ye(c), d = r - i, h = a - l, u = this.scaleVal, b = (-o + d) * (1 - e / u), v = (-s + h) * (1 - e / u);
  this.map.style.transform = `translate3d(${r - b}px, ${a - v}px, 0) scale(${e})`, this.scaleVal = e, this.bus.fire("scale", e);
}, fn = function() {
  const e = this.nodes.offsetHeight / this.container.offsetHeight, t = this.nodes.offsetWidth / this.container.offsetWidth, n = 1 / Math.max(1, Math.max(e, t));
  this.scaleVal = n;
  const { dx: o, dy: s } = Ce(this, !0);
  this.map.style.transform = `translate3d(${o}px, ${s}px, 0) scale(${n})`, this.bus.fire("scale", n);
}, un = function(e, t, n = !1) {
  const { map: o, scaleVal: s, bus: i, container: l, nodes: c } = this;
  if (n && o.style.transition === "transform 0.3s")
    return;
  const r = o.style.transform;
  let { x: a, y: d } = ye(r);
  const h = l.getBoundingClientRect(), u = c.getBoundingClientRect(), b = u.left < h.right && u.right > h.left, v = u.top < h.bottom && u.bottom > h.top;
  if (b) {
    const p = u.left + e, g = u.right + e;
    (p >= h.right || g <= h.left) && (e = 0);
  }
  if (v) {
    const p = u.top + t, g = u.bottom + t;
    (p >= h.bottom || g <= h.top) && (t = 0);
  }
  a += e, d += t, n && (o.style.transition = "transform 0.3s", setTimeout(() => {
    o.style.transition = "none";
  }, 300)), o.style.transform = `translate3d(${a}px, ${d}px, 0) scale(${s})`, i.fire("move", { dx: e, dy: t });
}, Ce = (e, t = !1) => {
  const { container: n, map: o, nodes: s } = e;
  let i, l;
  if (e.alignment === "nodes" || t)
    i = (n.offsetWidth - s.offsetWidth) / 2, l = (n.offsetHeight - s.offsetHeight) / 2, o.style.transformOrigin = "50% 50%";
  else {
    const c = o.querySelector("me-root"), r = c.offsetTop, a = c.offsetLeft, d = c.offsetWidth, h = c.offsetHeight;
    i = n.offsetWidth / 2 - a - d / 2, l = n.offsetHeight / 2 - r - h / 2, o.style.transformOrigin = `${a + d / 2}px 50%`;
  }
  return { dx: i, dy: l };
}, pn = function() {
  const { map: e, container: t } = this, { dx: n, dy: o } = Ce(this);
  t.scrollTop = 0, t.scrollLeft = 0, e.style.transform = `translate3d(${n}px, ${o}px, 0) scale(${this.scaleVal})`;
}, gn = function(e) {
  e(this);
}, mn = function(e) {
  e.nodeObj.parent && (this.clearSelection(), this.tempDirection === null && (this.tempDirection = this.direction), this.isFocusMode || (this.nodeDataBackup = this.nodeData, this.isFocusMode = !0), this.nodeData = e.nodeObj, this.initRight(), this.toCenter());
}, yn = function() {
  this.isFocusMode = !1, this.tempDirection !== null && (this.nodeData = this.nodeDataBackup, this.direction = this.tempDirection, this.tempDirection = null, this.refresh(), this.toCenter());
}, bn = function() {
  this.direction = 0, this.refresh(), this.toCenter(), this.bus.fire("changeDirection", this.direction);
}, vn = function() {
  this.direction = 1, this.refresh(), this.toCenter(), this.bus.fire("changeDirection", this.direction);
}, wn = function() {
  this.direction = 2, this.refresh(), this.toCenter(), this.bus.fire("changeDirection", this.direction);
}, xn = function(e, t) {
  const n = e.nodeObj;
  typeof t == "boolean" ? n.expanded = t : n.expanded !== !1 ? n.expanded = !1 : n.expanded = !0;
  const o = e.getBoundingClientRect(), s = {
    x: o.left,
    y: o.top
  }, i = e.parentNode, l = i.children[1];
  if (l.expanded = n.expanded, l.className = n.expanded ? "minus" : "", G(e), n.expanded) {
    const h = this.createChildren(
      n.children.map((u) => this.createWrapper(u).grp)
    );
    i.parentNode.appendChild(h);
  } else
    i.parentNode.children[1].remove();
  this.linkDiv(e.closest("me-main > me-wrapper"));
  const c = e.getBoundingClientRect(), r = {
    x: c.left,
    y: c.top
  }, a = s.x - r.x, d = s.y - r.y;
  this.move(a, d), this.bus.fire("expandNode", n);
}, En = function(e, t) {
  const n = e.nodeObj, o = e.getBoundingClientRect(), s = {
    x: o.left,
    y: o.top
  };
  F(n, t ?? !n.expanded), this.refresh();
  const i = this.findEle(n.id).getBoundingClientRect(), l = {
    x: i.left,
    y: i.top
  }, c = s.x - l.x, r = s.y - l.y;
  this.move(c, r);
}, Cn = function(e) {
  this.clearSelection(), e && (e = JSON.parse(JSON.stringify(e)), this.nodeData = e.nodeData, this.arrows = e.arrows || [], this.summaries = e.summaries || [], e.meta && (this.meta = e.meta), e.theme && this.changeTheme(e.theme)), R(this.nodeData), this.layout(), this.linkDiv();
}, Sn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  cancelFocus: yn,
  clearSelection: rn,
  disableEdit: dn,
  enableEdit: an,
  expandNode: xn,
  expandNodeAll: En,
  focusNode: mn,
  getData: cn,
  getDataString: ln,
  initLeft: bn,
  initRight: vn,
  initSide: wn,
  install: gn,
  move: un,
  refresh: Cn,
  scale: hn,
  scaleFit: fn,
  scrollIntoView: tn,
  selectNode: nn,
  selectNodes: on,
  stringifyData: Ee,
  toCenter: pn,
  unselectNodes: sn
}, Symbol.toStringTag, { value: "Module" })), Pe = "MIND-ELIXIR-WAIT-COPY", Nn = 40, Tn = 10, kn = ({ deltaMode: e, deltaY: t, viewportHeight: n }) => e === WheelEvent.DOM_DELTA_LINE ? t * Nn : e === WheelEvent.DOM_DELTA_PAGE ? t * n : t, _n = ({ deltaMode: e, deltaY: t, scaleSensitivity: n, viewportHeight: o }) => {
  const i = -kn({ deltaMode: e, deltaY: t, viewportHeight: o }) / Tn * n;
  return Math.max(-n, Math.min(n, i));
}, st = (e, t, n) => {
  t !== 0 && e.scale(e.scaleVal + t, n);
}, Dn = (e, t) => {
  const n = e.map.querySelectorAll(`.${t}>me-wrapper>me-parent>me-tpc`);
  n.length !== 0 && e.selectNode(n[Math.ceil(n.length / 2) - 1]);
}, Ln = (e) => {
  e.selectNode(e.map.querySelector("me-root>me-tpc"));
}, Mn = function(e, t) {
  const n = t.parentElement.parentElement.parentElement.previousSibling;
  if (n) {
    const o = n.firstChild;
    e.selectNode(o);
  }
}, An = function(e, t) {
  const n = t.parentElement.nextSibling;
  if (n && n.firstChild) {
    const o = n.firstChild.firstChild.firstChild;
    e.selectNode(o);
  }
}, Oe = function(e, t) {
  const n = e.currentNode || e.currentNodes?.[0];
  if (!n) return;
  const o = n.nodeObj, s = n.offsetParent.offsetParent.parentElement;
  o.parent ? s.className === t ? An(e, n) : o.parent?.parent ? Mn(e, n) : Ln(e) : Dn(e, t);
}, He = function(e, t) {
  const n = e.currentNode;
  if (!n || !n.nodeObj.parent) return;
  const s = t + "Sibling", i = n.parentElement.parentElement[s];
  i ? e.selectNode(i.firstChild.firstChild) : e.selectNode(n);
}, $e = function(e, t, n) {
  const o = t === "in" ? e.scaleSensitivity : -e.scaleSensitivity;
  st(e, o, n);
}, Pn = (e, t) => {
  const n = _n({
    deltaMode: t.deltaMode,
    deltaY: t.deltaY,
    scaleSensitivity: e.scaleSensitivity,
    viewportHeight: e.container.clientHeight || window.innerHeight
  });
  st(e, n, { x: t.clientX, y: t.clientY });
};
function On(e, t) {
  t = t === !0 ? {} : t;
  const n = () => {
    e.currentArrow ? e.removeArrow() : e.currentSummary ? e.removeSummary(e.currentSummary.summaryObj.id) : e.currentNodes && e.removeNodes(e.currentNodes);
  };
  let o = !1, s = null;
  const i = (r) => {
    const a = e.nodeData;
    if (r.key === "0")
      for (const d of a.children)
        F(d, !1);
    if (r.key === "=")
      for (const d of a.children)
        F(d, !0);
    if (["1", "2", "3", "4", "5", "6", "7", "8", "9"].includes(r.key))
      for (const d of a.children)
        F(d, !0, Number(r.key) - 1);
    e.refresh(), e.toCenter(), o = !1, s && (clearTimeout(s), s = null, e.container.removeEventListener("keydown", i));
  }, l = {
    Enter: (r) => {
      r.shiftKey ? e.insertSibling("before") : r.ctrlKey || r.metaKey ? e.insertParent() : e.insertSibling("after");
    },
    Tab: () => {
      e.addChild();
    },
    F1: () => {
      e.toCenter();
    },
    F2: () => {
      e.currentSummary ? e.editSummary(e.currentSummary) : e.currentArrow ? e.editArrowLabel(e.currentArrow) : e.beginEdit();
    },
    ArrowUp: (r) => {
      if (r.altKey)
        e.moveUpNode();
      else {
        if (r.metaKey || r.ctrlKey)
          return e.initSide();
        He(e, "previous");
      }
    },
    ArrowDown: (r) => {
      r.altKey ? e.moveDownNode() : He(e, "next");
    },
    ArrowLeft: (r) => {
      if (r.metaKey || r.ctrlKey)
        return e.initLeft();
      Oe(e, H.LHS);
    },
    ArrowRight: (r) => {
      if (r.metaKey || r.ctrlKey)
        return e.initRight();
      Oe(e, H.RHS);
    },
    PageUp: () => e.moveUpNode(),
    PageDown: () => {
      e.moveDownNode();
    },
    "=": (r) => {
      (r.metaKey || r.ctrlKey) && $e(e, "in");
    },
    "-": (r) => {
      (r.metaKey || r.ctrlKey) && $e(e, "out");
    },
    0: (r) => {
      if (r.metaKey || r.ctrlKey) {
        if (o)
          return;
        e.scale(1);
      }
    },
    k: (r) => {
      (r.metaKey || r.ctrlKey) && (o = !0, s && (clearTimeout(s), e.container.removeEventListener("keydown", i)), s = window.setTimeout(() => {
        o = !1, s = null;
      }, 2e3), e.container.addEventListener("keydown", i));
    },
    Delete: n,
    Backspace: n,
    ...t
  };
  e.container.onkeydown = (r) => {
    if ((r.ctrlKey || r.metaKey) && ["c", "v", "x"].includes(r.key) || r.preventDefault(), !e.editable) return;
    const d = l[r.key];
    d && d(r);
  };
  const c = (r) => {
    if (r.target instanceof HTMLElement && r.target.id === "input-box" || e.currentNodes.length === 0) return !1;
    if (r.clipboardData) {
      const a = me(e.currentNodes).map((h) => h.nodeObj), d = Ee({
        magic: Pe,
        data: a
      });
      return r.clipboardData.setData("text/plain", d), r.preventDefault(), !0;
    }
    return !1;
  };
  e.container.addEventListener("copy", c), e.container.addEventListener("cut", (r) => {
    c(r) && n();
  }), e.container.addEventListener("paste", (r) => {
    const a = r.clipboardData?.getData("text/plain");
    if (a)
      try {
        const d = JSON.parse(a);
        if (d && d.magic === Pe && Array.isArray(d.data)) {
          const h = d.data, u = h.map((b) => ({ nodeObj: b }));
          h.length > 0 && e.currentNode && (e.copyNodes(u, e.currentNode), r.preventDefault());
          return;
        }
      } catch {
      }
    e.pasteHandler && e.pasteHandler(r);
  });
}
function Hn(e) {
  const { panHelper: t, container: n } = e;
  let o = null;
  e.spacePressed = !1;
  const s = {
    lastTap: 0,
    lastTapTarget: null,
    DOUBLE_CLICK_THRESHOLD: 300,
    detect(f, y) {
      if (f.button !== 0) {
        this.clear();
        return;
      }
      const x = (/* @__PURE__ */ new Date()).getTime(), S = x - this.lastTap, C = S < this.DOUBLE_CLICK_THRESHOLD && S > 0 && this.lastTapTarget === f.target;
      this.lastTap = x, this.lastTapTarget = f.target, C && y(f);
    },
    clear() {
      this.lastTap = 0, this.lastTapTarget = null;
    }
  }, i = {
    Idle: 0,
    Pinch: 1,
    DragWait: 2,
    Drag: 3,
    Pan: 4,
    BoxSelect: 5
  };
  e.ptState = i.Idle;
  const l = {
    lastDistance: null,
    activePointers: /* @__PURE__ */ new Map(),
    handlePointerDown(f) {
      if (f.pointerType !== "touch") return !1;
      if (this.activePointers.set(f.pointerId, { x: f.clientX, y: f.clientY }), this.activePointers.size >= 2) {
        const [y, x] = Array.from(this.activePointers.values());
        return this.lastDistance = De(y, x), !0;
      }
      return !1;
    },
    handlePointerMove(f) {
      if (f.pointerType !== "touch" || !this.activePointers.has(f.pointerId)) return !1;
      if (this.activePointers.set(f.pointerId, { x: f.clientX, y: f.clientY }), this.activePointers.size >= 2) {
        const [y, x] = Array.from(this.activePointers.values()), S = De(y, x);
        if (this.lastDistance !== null && this.lastDistance > 0) {
          const C = S / this.lastDistance;
          e.scale(e.scaleVal * C, {
            x: (y.x + x.x) / 2,
            y: (y.y + x.y) / 2
          });
        }
        return this.lastDistance = S, !0;
      }
      return !1;
    },
    handlePointerUp(f) {
      f.pointerType === "touch" && (this.activePointers.delete(f.pointerId), this.activePointers.size < 2 && (this.lastDistance = null));
    },
    clear() {
      this.activePointers.clear(), this.lastDistance = null;
    }
  }, c = wt(e), r = {
    timer: null,
    startPos: null,
    pointerId: null,
    DURATION: 500,
    MOVE_THRESHOLD: 10,
    clear() {
      this.timer !== null && (clearTimeout(this.timer), this.timer = null, this.startPos = null, this.pointerId = null);
    },
    start(f, y) {
      this.timer = window.setTimeout(() => {
        y(f), this.timer = null, this.startPos = null, this.pointerId = null;
      }, this.DURATION), this.startPos = { x: f.clientX, y: f.clientY }, this.pointerId = f.pointerId;
    },
    handleMove(f) {
      if (this.timer !== null && this.startPos !== null && f.pointerId === this.pointerId) {
        const y = f.clientX - this.startPos.x, x = f.clientY - this.startPos.y;
        Math.sqrt(y * y + x * x) > this.MOVE_THRESHOLD && this.clear();
      }
    }
  }, a = (f, y) => {
    if (f.closest("#input-box")) return !1;
    const x = f.closest(".svg-label"), S = f.closest(".topiclinks, .summary"), C = x ? { type: x.dataset.type, element: document.getElementById(x.dataset.svgId) } : S ? { type: S.classList.contains("topiclinks") ? "arrow" : "summary", element: f.closest("g") } : null;
    if (!C?.type || !C?.element) return !1;
    const { type: T, element: D } = C;
    return e.clearSelection(), T === "arrow" ? y ? e.editArrowLabel(D) : e.selectArrow(D) : y ? e.editSummary(D) : e.selectSummary(D), !0;
  }, d = (f) => {
    if (f.pointerType === "mouse" && f.button !== 0) return;
    if (e.helper1?.moved) {
      e.helper1.clear();
      return;
    }
    if (e.helper2?.moved) {
      e.helper2.clear();
      return;
    }
    if (t.moved) {
      t.clear();
      return;
    }
    if (c?.isDragging)
      return;
    const y = f.target;
    y.tagName === "ME-EPD" && (f.ctrlKey || f.metaKey ? e.expandNodeAll(y.previousSibling) : e.expandNode(y.previousSibling));
  }, h = (f) => {
    if (!e.editable) return;
    const y = f.target;
    if (te(y)) {
      e.selectNode(y), e.beginEdit(y);
      return;
    }
    a(y, !0);
  }, u = (f) => {
    if (f.pointerType === "touch" && l.handlePointerDown(f)) {
      e.ptState = i.Pinch, r.clear(), t.clear(), (c.isDragging || c.pointerId !== null) && Ae(e, c);
      return;
    }
    if (e.ptState === i.Pinch) return;
    const y = f.target;
    if (e.editable && y.className === "map-container" && f.button === 0 && f.pointerType === "mouse") {
      e.ptState = i.BoxSelect;
      return;
    }
    if (t.handlePointerDown(f), t.mousedown && (e.ptState = i.Pan), f.button === 0 || f.pointerType === "touch")
      if (te(y)) {
        e.selection?.cancel();
        const S = e.currentNodes || [];
        if (f.ctrlKey || f.metaKey || e.mobileMultiSelect ? S.includes(y) ? o = y : ((e.currentArrow || e.currentSummary) && e.clearSelection(), e.selection?.select(y)) : S.includes(y) || e.selectNode(y), !e.editable) return;
        f.pointerType === "touch" ? (e.ptState = i.DragWait, r.start(f, (T) => {
          Me(e, c, T, !0) && (e.ptState = i.Drag, y.setPointerCapture(T.pointerId));
        })) : Me(e, c, f, !1) && (e.ptState = i.Drag, y.setPointerCapture(f.pointerId));
      } else
        a(y, !1);
  }, b = (f) => {
    switch (e.ptState) {
      case i.Pinch:
        l.handlePointerMove(f);
        break;
      case i.DragWait:
        r.handleMove(f), r.timer === null && (e.ptState = i.Idle);
        break;
      case i.Drag:
        Et(e, c, f);
        break;
      case i.Pan:
        t.handlePointerMove(f);
        break;
    }
  }, v = (f) => {
    f.pointerType === "touch" && l.handlePointerUp(f);
    const y = c.isDragging, x = t.moved;
    switch (e.ptState) {
      case i.DragWait:
        r.clear();
        break;
      case i.Drag:
        Ct(e, c, f);
        break;
      case i.Pan:
        t.handlePointerUp(f);
        break;
    }
    s.detect(f, h), (e.ptState !== i.Pinch || l.activePointers.size < 2) && (e.ptState = i.Idle), o && (!y && !x && e.selection?.deselect(o), o = null);
  }, p = () => {
    l.clear(), r.clear(), t.clear(), s.clear(), (c.isDragging || c.pointerId !== null) && Ae(e, c), e.ptState = i.Idle, o = null;
  }, g = (f) => {
    f.preventDefault(), f.button === 2 && e.editable && setTimeout(() => {
      if (e.panHelper.moved || e.ptState !== i.Idle && e.ptState !== i.Pan) return;
      const y = f.target;
      te(y) && !y.classList.contains("selected") && e.selectNode(y), e.bus.fire("showContextMenu", f);
    }, 200);
  }, m = (f) => {
    if (f.stopPropagation(), f.preventDefault(), f.ctrlKey || f.metaKey) return Pn(e, f);
    if (f.shiftKey) return e.move(-f.deltaY, 0);
    e.move(-f.deltaX, -f.deltaY);
  }, w = (f) => {
    f.code === "Space" && (e.spacePressed = !0, e.container.classList.add("space-pressed"));
  }, E = (f) => {
    f.code === "Space" && (e.spacePressed = !1, e.container.classList.remove("space-pressed"));
  };
  return qe([
    { dom: n, evt: "pointerdown", func: u },
    { dom: n, evt: "pointermove", func: b },
    { dom: n, evt: "pointerup", func: v },
    { dom: n, evt: "pointercancel", func: p },
    { dom: n, evt: "click", func: d },
    { dom: n, evt: "contextmenu", func: g },
    { dom: n, evt: "wheel", func: typeof e.handleWheel == "function" ? e.handleWheel : m },
    { dom: n, evt: "blur", func: p },
    { dom: n, evt: "keydown", func: w },
    { dom: n, evt: "keyup", func: E }
  ]);
}
function $n() {
  return {
    handlers: {},
    addListener: function(e, t) {
      this.handlers[e] === void 0 && (this.handlers[e] = []), this.handlers[e].push(t);
    },
    fire: function(e, ...t) {
      if (this.handlers[e] instanceof Array) {
        const n = this.handlers[e];
        for (let o = 0; o < n.length; o++)
          n[o](...t);
      }
    },
    removeListener: function(e, t) {
      if (!this.handlers[e]) return;
      const n = this.handlers[e];
      if (!t)
        n.length = 0;
      else if (n.length)
        for (let o = 0; o < n.length; o++)
          n[o] === t && this.handlers[e].splice(o, 1);
    }
  };
}
const A = "http://www.w3.org/2000/svg", re = function(e) {
  const t = e.clientWidth, n = e.clientHeight, o = e.dataset, s = Number(o.x), i = Number(o.y), l = o.anchor;
  let c = s;
  l === "middle" ? c = s - t / 2 : l === "end" && (c = s - t), e.style.left = `${c}px`, e.style.top = `${i - n / 2}px`, e.style.visibility = "visible";
}, de = function(e, t, n, o) {
  const { anchor: s = "middle", color: i, dataType: l, svgId: c } = o, r = document.createElement("div");
  r.className = "svg-label", r.style.color = i || "#666";
  const a = "label-" + c;
  return r.id = a, r.innerHTML = e, r.dataset.type = l, r.dataset.svgId = c, r.dataset.x = t.toString(), r.dataset.y = n.toString(), r.dataset.anchor = s, r;
}, it = function(e, t, n) {
  const o = document.createElementNS(A, "path");
  return k(o, {
    d: e,
    stroke: t || "#666",
    fill: "none",
    "stroke-width": n
  }), o;
}, z = function(e) {
  const t = document.createElementNS(A, "svg");
  return t.setAttribute("class", e), t.setAttribute("overflow", "visible"), t;
}, je = function() {
  const e = document.createElementNS(A, "line");
  return e.setAttribute("stroke", "#4dc4ff"), e.setAttribute("fill", "none"), e.setAttribute("stroke-width", "2"), e.setAttribute("opacity", "0.45"), e;
}, jn = function(e, t, n, o) {
  const s = document.createElementNS(A, "g");
  return [
    {
      name: "line",
      d: e
    },
    {
      name: "arrow1",
      d: t
    },
    {
      name: "arrow2",
      d: n
    }
  ].forEach((l, c) => {
    const r = l.d, a = document.createElementNS(A, "path"), d = {
      d: r,
      stroke: o?.stroke || "rgb(227, 125, 116)",
      fill: "none",
      "stroke-linecap": o?.strokeLinecap || "cap",
      "stroke-width": String(o?.strokeWidth || "2")
    };
    o?.opacity !== void 0 && (d.opacity = String(o.opacity)), k(a, d), c === 0 && a.setAttribute("stroke-dasharray", o?.strokeDasharray || "8,2");
    const h = document.createElementNS(A, "path");
    k(h, {
      d: r,
      stroke: "transparent",
      fill: "none",
      "stroke-width": "15"
    }), s.appendChild(h), s.appendChild(a), s[l.name] = a;
  }), s;
}, rt = function(e, t, n) {
  if (!t) return;
  const o = n.label;
  t.style.opacity = "0";
  const s = t.cloneNode(!0);
  e.nodes.appendChild(s), s.id = "input-box", s.textContent = o, s.contentEditable = "plaintext-only", s.spellcheck = !1, s.style.cssText = `
    left:${t.style.left};
    top:${t.style.top}; 
    max-width: 200px;
  `, Qe(s), e.scrollIntoView(s), s.addEventListener("keydown", (i) => {
    i.stopPropagation();
    const l = i.key;
    if (l === "Enter" || l === "Tab") {
      if (i.shiftKey) return;
      i.preventDefault(), s.blur(), e.container.focus();
    }
  }), s.addEventListener("blur", () => {
    if (!s) return;
    const i = s.innerText?.trim() || "";
    i === "" ? n.label = o : n.label = i, t.style.opacity = "1", s.remove(), i !== o && (e.markdown ? t.innerHTML = e.markdown(n.label, n) : t.textContent = n.label, re(t), "parent" in n ? e.bus.fire("operation", {
      name: "finishEditSummary",
      obj: n
    }) : e.bus.fire("operation", {
      name: "finishEditArrowLabel",
      obj: n
    }));
  });
}, In = function(e) {
  const t = this.map.querySelector("me-root"), n = t.offsetTop, o = t.offsetLeft, s = t.offsetWidth, i = t.offsetHeight, l = this.map.querySelectorAll("me-main > me-wrapper");
  this.lines.innerHTML = "";
  for (let c = 0; c < l.length; c++) {
    const r = l[c], a = r.querySelector("me-tpc"), { offsetLeft: d, offsetTop: h } = M(this.nodes, a), u = a.offsetWidth, b = a.offsetHeight, v = r.parentNode.className, p = this.generateMainBranch({ pT: n, pL: o, pW: s, pH: i, cT: h, cL: d, cW: u, cH: b, direction: v, containerHeight: this.nodes.offsetHeight }), g = this.theme.palette, m = a.nodeObj.branchColor || g[c % g.length];
    if (a.style.borderColor = m, this.lines.appendChild(it(p, m, "3")), e && e !== r)
      continue;
    const w = z("subLines"), E = r.lastChild;
    E.tagName === "svg" && E.remove(), r.appendChild(w), lt(this, w, m, r, v, !0);
  }
  this.labelContainer.innerHTML = "", this.renderArrow(), this.renderSummary(), this.bus.fire("linkDiv");
}, lt = function(e, t, n, o, s, i) {
  const l = o.firstChild, c = o.children[1].children;
  if (c.length === 0) return;
  const r = l.offsetTop, a = l.offsetLeft, d = l.offsetWidth, h = l.offsetHeight;
  for (let u = 0; u < c.length; u++) {
    const b = c[u], v = b.firstChild, p = v.offsetTop, g = v.offsetLeft, m = v.offsetWidth, w = v.offsetHeight, E = v.firstChild.nodeObj.branchColor || n, N = e.generateSubBranch({ pT: r, pL: a, pW: d, pH: h, cT: p, cL: g, cW: m, cH: w, direction: s, isFirst: i });
    t.appendChild(it(N, E, "2"));
    const f = v.children[1];
    if (f) {
      if (!f.expanded) continue;
    } else
      continue;
    lt(e, t, E, b, s);
  }
}, Rn = {
  addChild: "Add child",
  addParent: "Add parent",
  addSibling: "Add sibling",
  removeNode: "Remove node",
  focus: "Focus Mode",
  cancelFocus: "Cancel Focus Mode",
  moveUp: "Move up",
  moveDown: "Move down",
  link: "Link",
  linkBidirectional: "Bidirectional Link",
  clickTips: "Please click the target node",
  summary: "Summary"
};
function Bn(e, t) {
  const n = {
    focus: !0,
    link: !0,
    locale: Rn
  };
  t = t === !0 ? n : Object.assign(n, t);
  const o = (y) => {
    const x = document.createElement("div");
    return x.innerText = y, x.className = "tips", x;
  }, s = (y, x, S) => {
    const C = document.createElement("li");
    return C.id = y, C.innerHTML = `<span>${ae(x)}</span><span ${S ? 'class="key"' : ""}>${ae(S)}</span>`, C;
  }, i = t.locale, l = s("cm-add_child", i.addChild, "Tab"), c = s("cm-add_parent", i.addParent, "Ctrl + Enter"), r = s("cm-add_sibling", i.addSibling, "Enter"), a = s("cm-remove_child", i.removeNode, "Delete"), d = s("cm-fucus", i.focus, ""), h = s("cm-unfucus", i.cancelFocus, ""), u = s("cm-up", i.moveUp, "PgUp"), b = s("cm-down", i.moveDown, "Pgdn"), v = s("cm-link", i.link, ""), p = s("cm-link-bidirectional", i.linkBidirectional, ""), g = s("cm-summary", i.summary, ""), m = document.createElement("ul");
  if (m.className = "menu-list", m.appendChild(l), m.appendChild(c), m.appendChild(r), m.appendChild(a), t.focus && (m.appendChild(d), m.appendChild(h)), m.appendChild(u), m.appendChild(b), m.appendChild(g), t.link && (m.appendChild(v), m.appendChild(p)), t && t.extend)
    for (let y = 0; y < t.extend.length; y++) {
      const x = t.extend[y], S = s(x.name, x.name, x.key || "");
      m.appendChild(S), S.onclick = (C) => {
        x.onclick(C);
      };
    }
  const w = document.createElement("div");
  w.className = "context-menu", w.appendChild(m), w.hidden = !0, e.container.append(w);
  let E = !0;
  const N = (y) => {
    const x = y.target;
    if (te(x)) {
      x.parentElement.tagName === "ME-ROOT" ? E = !0 : E = !1, E ? (d.className = "disabled", u.className = "disabled", b.className = "disabled", c.className = "disabled", r.className = "disabled", a.className = "disabled") : (d.className = "", u.className = "", b.className = "", c.className = "", r.className = "", a.className = ""), w.hidden = !1, m.style.top = "", m.style.bottom = "", m.style.left = "", m.style.right = "";
      const S = m.offsetHeight, C = m.offsetWidth, T = m.getBoundingClientRect(), D = y.clientY - T.top, L = y.clientX - T.left;
      S + D > window.innerHeight ? (m.style.top = "", m.style.bottom = "0px") : (m.style.bottom = "", m.style.top = D + 15 + "px"), C + L > window.innerWidth ? (m.style.left = "", m.style.right = "0px") : (m.style.right = "", m.style.left = L + 10 + "px");
    }
  };
  e.bus.addListener("showContextMenu", N), w.onclick = (y) => {
    y.target === w && (w.hidden = !0);
  }, l.onclick = () => {
    e.addChild(), w.hidden = !0;
  }, c.onclick = () => {
    e.insertParent(), w.hidden = !0;
  }, r.onclick = () => {
    E || (e.insertSibling("after"), w.hidden = !0);
  }, a.onclick = () => {
    E || (e.removeNodes(e.currentNodes || []), w.hidden = !0);
  }, d.onclick = () => {
    E || (e.focusNode(e.currentNode), w.hidden = !0);
  }, h.onclick = () => {
    e.cancelFocus(), w.hidden = !0;
  }, u.onclick = () => {
    E || (e.moveUpNode(), w.hidden = !0);
  }, b.onclick = () => {
    E || (e.moveDownNode(), w.hidden = !0);
  };
  const f = (y) => {
    w.hidden = !0;
    const x = e.currentNode, S = o(i.clickTips);
    e.container.appendChild(S), e.map.addEventListener(
      "click",
      (C) => {
        C.preventDefault(), S.remove();
        const T = C.target;
        (T.parentElement.tagName === "ME-PARENT" || T.parentElement.tagName === "ME-ROOT") && e.createArrow(x, T, y);
      },
      {
        once: !0
      }
    );
  };
  return v.onclick = () => f(), p.onclick = () => f({ bidirectional: !0 }), g.onclick = () => {
    w.hidden = !0, e.createSummary(), e.unselectNodes(e.currentNodes);
  }, () => {
    l.onclick = null, c.onclick = null, r.onclick = null, a.onclick = null, d.onclick = null, h.onclick = null, u.onclick = null, b.onclick = null, v.onclick = null, g.onclick = null, w.onclick = null, e.container.oncontextmenu = null;
  };
}
const Wn = function(e) {
  return ["createSummary", "removeSummary", "finishEditSummary"].includes(e.name) ? {
    type: "summary",
    value: e.obj.id
  } : ["createArrow", "removeArrow", "finishEditArrowLabel"].includes(e.name) ? {
    type: "arrow",
    value: e.obj.id
  } : ["removeNodes", "copyNodes", "moveNodeBefore", "moveNodeAfter", "moveNodeIn"].includes(e.name) ? {
    type: "nodes",
    value: e.objs.map((t) => t.id)
  } : {
    type: "nodes",
    value: [e.obj.id]
  };
};
function Yn(e) {
  let t = [], n = -1, o = e.getData(), s = [];
  e.undo = function() {
    if (n > -1) {
      const r = t[n];
      o = r.prev, e.refresh(r.prev);
      try {
        r.currentTarget.type === "nodes" && (r.operation === "removeNodes" ? e.selectNodes(r.currentTarget.value.map((a) => this.findEle(a))) : e.selectNodes(r.currentSelected.map((a) => this.findEle(a))));
      } catch {
      } finally {
        n--;
      }
    }
  }, e.redo = function() {
    if (n < t.length - 1) {
      n++;
      const r = t[n];
      o = r.next, e.refresh(r.next);
      try {
        r.currentTarget.type === "nodes" && (r.operation === "removeNodes" ? e.selectNodes(r.currentSelected.map((a) => this.findEle(a))) : e.selectNodes(r.currentTarget.value.map((a) => this.findEle(a))));
      } catch {
      }
    }
  }, e.clearHistory = function() {
    t = [], n = -1, o = e.getData(), e.clearSelection();
  };
  const i = function(r) {
    if (r.name === "beginEdit") return;
    t = t.slice(0, n + 1);
    const a = e.getData(), d = {
      prev: o,
      operation: r.name,
      currentSelected: s.map((h) => h.id),
      currentTarget: Wn(r),
      next: a
    };
    t.push(d), o = a, n = t.length - 1;
  }, l = function(r) {
    (r.metaKey || r.ctrlKey) && (r.shiftKey && r.key === "Z" || r.key === "y") ? e.redo() : (r.metaKey || r.ctrlKey) && r.key === "z" && e.undo();
  }, c = function() {
    s = e.currentNodes.map((r) => r.nodeObj);
  };
  return e.bus.addListener("operation", i), e.bus.addListener("selectNodes", c), e.container.addEventListener("keydown", l), () => {
    e.bus.removeListener("operation", i), e.bus.removeListener("selectNodes", c), e.container.removeEventListener("keydown", l);
  };
}
const Xn = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169394918" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2021" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M851.91168 328.45312c-59.97056 0-108.6208 48.47104-108.91264 108.36992l-137.92768 38.4a109.14304 109.14304 0 0 0-63.46752-46.58688l1.39264-137.11872c47.29344-11.86816 82.31936-54.66624 82.31936-105.64096 0-60.15488-48.76288-108.91776-108.91776-108.91776s-108.91776 48.76288-108.91776 108.91776c0 49.18784 32.60928 90.75712 77.38368 104.27392l-1.41312 138.87488a109.19936 109.19936 0 0 0-63.50336 48.55808l-138.93632-39.48544 0.01024-0.72704c0-60.15488-48.76288-108.91776-108.91776-108.91776s-108.91776 48.75776-108.91776 108.91776c0 60.15488 48.76288 108.91264 108.91776 108.91264 39.3984 0 73.91232-20.92032 93.03552-52.2496l139.19232 39.552-0.00512 0.2304c0 25.8304 9.00096 49.5616 24.02816 68.23424l-90.14272 132.63872a108.7488 108.7488 0 0 0-34.2528-5.504c-60.15488 0-108.91776 48.768-108.91776 108.91776 0 60.16 48.76288 108.91776 108.91776 108.91776 60.16 0 108.92288-48.75776 108.92288-108.91776 0-27.14624-9.9328-51.968-26.36288-71.04l89.04704-131.03104a108.544 108.544 0 0 0 37.6832 6.70208 108.672 108.672 0 0 0 36.48512-6.272l93.13792 132.57216a108.48256 108.48256 0 0 0-24.69888 69.0688c0 60.16 48.768 108.92288 108.91776 108.92288 60.16 0 108.91776-48.76288 108.91776-108.92288 0-60.14976-48.75776-108.91776-108.91776-108.91776a108.80512 108.80512 0 0 0-36.69504 6.3488l-93.07136-132.48a108.48768 108.48768 0 0 0 24.79616-72.22784l136.09984-37.888c18.99008 31.93856 53.84192 53.3504 93.69088 53.3504 60.16 0 108.92288-48.75776 108.92288-108.91264-0.00512-60.15488-48.77312-108.92288-108.92288-108.92288z" p-id="2022"></path></svg>', Fn = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169375313" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1775" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M639 463.30000001L639 285.1c0-36.90000001-26.4-68.5-61.3-68.5l-150.2 0c-1.5 0-3 0.1-4.5 0.3-10.2-38.7-45.5-67.3-87.5-67.3-50 0-90.5 40.5-90.5 90.5s40.5 90.5 90.5 90.5c42 0 77.3-28.6 87.5-67.39999999 1.4 0.3 2.9 0.4 4.5 0.39999999L577.7 263.6c6.8 0 14.3 8.9 14.3 21.49999999l0 427.00000001c0 12.7-7.40000001 21.5-14.30000001 21.5l-150.19999999 0c-1.5 0-3 0.2-4.5 0.4-10.2-38.8-45.5-67.3-87.5-67.3-50 0-90.5 40.5-90.5 90.4 0 49.9 40.5 90.6 90.5 90.59999999 42 0 77.3-28.6 87.5-67.39999999 1.4 0.2 2.9 0.4 4.49999999 0.4L577.7 780.7c34.80000001 0 61.3-31.6 61.3-68.50000001L639 510.3l79.1 0c10.4 38.5 45.49999999 67 87.4 67 50 0 90.5-40.5 90.5-90.5s-40.5-90.5-90.5-90.5c-41.79999999 0-77.00000001 28.4-87.4 67L639 463.30000001z" fill="currentColor" p-id="1776"></path></svg>', Kn = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169667709" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="3037" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M385 560.69999999L385 738.9c0 36.90000001 26.4 68.5 61.3 68.5l150.2 0c1.5 0 3-0.1 4.5-0.3 10.2 38.7 45.5 67.3 87.5 67.3 50 0 90.5-40.5 90.5-90.5s-40.5-90.5-90.5-90.5c-42 0-77.3 28.6-87.5 67.39999999-1.4-0.3-2.9-0.4-4.5-0.39999999L446.3 760.4c-6.8 0-14.3-8.9-14.3-21.49999999l0-427.00000001c0-12.7 7.40000001-21.5 14.30000001-21.5l150.19999999 0c1.5 0 3-0.2 4.5-0.4 10.2 38.8 45.5 67.3 87.5 67.3 50 0 90.5-40.5 90.5-90.4 0-49.9-40.5-90.6-90.5-90.59999999-42 0-77.3 28.6-87.5 67.39999999-1.4-0.2-2.9-0.4-4.49999999-0.4L446.3 243.3c-34.80000001 0-61.3 31.6-61.3 68.50000001L385 513.7l-79.1 0c-10.4-38.5-45.49999999-67-87.4-67-50 0-90.5 40.5-90.5 90.5s40.5 90.5 90.5 90.5c41.79999999 0 77.00000001-28.4 87.4-67L385 560.69999999z" fill="currentColor" p-id="3038"></path></svg>', Vn = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169402629" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2170" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M639.328 416c8.032 0 16.096-3.008 22.304-9.056l202.624-197.184-0.8 143.808c-0.096 17.696 14.144 32.096 31.808 32.192 0.064 0 0.128 0 0.192 0 17.6 0 31.904-14.208 32-31.808l1.248-222.208c0-0.672-0.352-1.248-0.384-1.92 0.032-0.512 0.288-0.896 0.288-1.408 0.032-17.664-14.272-32-31.968-32.032L671.552 96l-0.032 0c-17.664 0-31.968 14.304-32 31.968C639.488 145.632 653.824 160 671.488 160l151.872 0.224-206.368 200.8c-12.672 12.32-12.928 32.608-0.64 45.248C622.656 412.736 630.976 416 639.328 416z" p-id="2171"></path><path d="M896.032 639.552 896.032 639.552c-17.696 0-32 14.304-32.032 31.968l-0.224 151.872-200.832-206.4c-12.32-12.64-32.576-12.96-45.248-0.64-12.672 12.352-12.928 32.608-0.64 45.248l197.184 202.624-143.808-0.8c-0.064 0-0.128 0-0.192 0-17.6 0-31.904 14.208-32 31.808-0.096 17.696 14.144 32.096 31.808 32.192l222.24 1.248c0.064 0 0.128 0 0.192 0 0.64 0 1.12-0.32 1.76-0.352 0.512 0.032 0.896 0.288 1.408 0.288l0.032 0c17.664 0 31.968-14.304 32-31.968L928 671.584C928.032 653.952 913.728 639.584 896.032 639.552z" p-id="2172"></path><path d="M209.76 159.744l143.808 0.8c0.064 0 0.128 0 0.192 0 17.6 0 31.904-14.208 32-31.808 0.096-17.696-14.144-32.096-31.808-32.192L131.68 95.328c-0.064 0-0.128 0-0.192 0-0.672 0-1.248 0.352-1.888 0.384-0.448 0-0.8-0.256-1.248-0.256 0 0-0.032 0-0.032 0-17.664 0-31.968 14.304-32 31.968L96 352.448c-0.032 17.664 14.272 32 31.968 32.032 0 0 0.032 0 0.032 0 17.664 0 31.968-14.304 32-31.968l0.224-151.936 200.832 206.4c6.272 6.464 14.624 9.696 22.944 9.696 8.032 0 16.096-3.008 22.304-9.056 12.672-12.32 12.96-32.608 0.64-45.248L209.76 159.744z" p-id="2173"></path><path d="M362.368 617.056l-202.624 197.184 0.8-143.808c0.096-17.696-14.144-32.096-31.808-32.192-0.064 0-0.128 0-0.192 0-17.6 0-31.904 14.208-32 31.808l-1.248 222.24c0 0.704 0.352 1.312 0.384 2.016 0 0.448-0.256 0.832-0.256 1.312-0.032 17.664 14.272 32 31.968 32.032L352.448 928c0 0 0.032 0 0.032 0 17.664 0 31.968-14.304 32-31.968s-14.272-32-31.968-32.032l-151.936-0.224 206.4-200.832c12.672-12.352 12.96-32.608 0.64-45.248S375.008 604.704 362.368 617.056z" p-id="2174"></path></svg>', zn = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169573443" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2883" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M514.133333 488.533333m-106.666666 0a106.666667 106.666667 0 1 0 213.333333 0 106.666667 106.666667 0 1 0-213.333333 0Z" fill="currentColor" p-id="2884"></path><path d="M512 64C264.533333 64 64 264.533333 64 512c0 236.8 183.466667 428.8 416 445.866667v-134.4c-53.333333-59.733333-200.533333-230.4-200.533333-334.933334 0-130.133333 104.533333-234.666667 234.666666-234.666666s234.666667 104.533333 234.666667 234.666666c0 61.866667-49.066667 153.6-145.066667 270.933334l-59.733333 68.266666V960C776.533333 942.933333 960 748.8 960 512c0-247.466667-200.533333-448-448-448z" fill="currentColor" p-id="2885"></path></svg>', Gn = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169419447" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2480" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M863.328 482.56l-317.344-1.12L545.984 162.816c0-17.664-14.336-32-32-32s-32 14.336-32 32l0 318.4L159.616 480.064c-0.032 0-0.064 0-0.096 0-17.632 0-31.936 14.24-32 31.904C127.424 529.632 141.728 544 159.392 544.064l322.592 1.152 0 319.168c0 17.696 14.336 32 32 32s32-14.304 32-32l0-318.944 317.088 1.12c0.064 0 0.096 0 0.128 0 17.632 0 31.936-14.24 32-31.904C895.264 496.992 880.96 482.624 863.328 482.56z" p-id="2481"></path></svg>', qn = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169426515" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2730" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M863.744 544 163.424 544c-17.664 0-32-14.336-32-32s14.336-32 32-32l700.32 0c17.696 0 32 14.336 32 32S881.44 544 863.744 544z" p-id="2731"></path></svg>', Un = {
  side: Xn,
  left: Fn,
  right: Kn,
  full: Vn,
  living: zn,
  zoomin: Gn,
  zoomout: qn
}, I = (e, t) => {
  const n = document.createElement("span");
  return n.id = e, n.innerHTML = Un[t], n;
};
function Jn(e) {
  const t = document.createElement("div"), n = I("fullscreen", "full"), o = I("toCenter", "living"), s = I("zoomout", "zoomout"), i = I("zoomin", "zoomin");
  t.appendChild(n), t.appendChild(o), t.appendChild(s), t.appendChild(i), t.className = "mind-elixir-toolbar rb";
  let l = null;
  const c = () => {
    const a = e.container.getBoundingClientRect(), d = ye(e.map.style.transform), h = a.width / 2, u = a.height / 2, b = (h - d.x) / e.scaleVal, v = (u - d.y) / e.scaleVal;
    l = {
      containerRect: a,
      currentTransform: d,
      mapCenterX: b,
      mapCenterY: v
    };
  }, r = () => {
    if (l) {
      const a = e.container.getBoundingClientRect(), d = a.width / 2, h = a.height / 2, u = d - l.mapCenterX * e.scaleVal, b = h - l.mapCenterY * e.scaleVal, v = u - l.currentTransform.x, p = b - l.currentTransform.y;
      e.move(v, p);
    }
  };
  return e.el.addEventListener("fullscreenchange", r), n.onclick = () => {
    c(), document.fullscreenElement !== e.el ? e.el.requestFullscreen() : document.exitFullscreen();
  }, o.onclick = () => {
    e.toCenter();
  }, s.onclick = () => {
    e.scale(e.scaleVal - e.scaleSensitivity);
  }, i.onclick = () => {
    e.scale(e.scaleVal + e.scaleSensitivity);
  }, t;
}
function Zn(e) {
  const t = document.createElement("div"), n = I("tbltl", "left"), o = I("tbltr", "right"), s = I("tblts", "side");
  return t.appendChild(n), t.appendChild(o), t.appendChild(s), t.className = "mind-elixir-toolbar lt", n.onclick = () => {
    e.initLeft();
  }, o.onclick = () => {
    e.initRight();
  }, s.onclick = () => {
    e.initSide();
  }, t;
}
function Qn(e) {
  e.container.append(Jn(e)), e.container.append(Zn(e));
}
class eo {
  _listeners = /* @__PURE__ */ new Map();
  addEventListener(t, n) {
    const o = this._listeners.get(t) ?? /* @__PURE__ */ new Set();
    return this._listeners.set(t, o), o.add(n), this;
  }
  removeEventListener(t, n) {
    return this._listeners.get(t)?.delete(n), this;
  }
  dispatchEvent(t, ...n) {
    let o = !0;
    for (const s of this._listeners.get(t) ?? [])
      o = s(...n) !== !1 && o;
    return o;
  }
  unbindAllListeners() {
    this._listeners.clear();
  }
  // Let's also support on, off and emit like node
  on = this.addEventListener;
  off = this.removeEventListener;
  emit = this.dispatchEvent;
}
const Ie = (e, t = "px") => typeof e == "number" ? e + t : e, $ = ({ style: e }, t, n) => {
  if (typeof t == "object")
    for (const [o, s] of Object.entries(t))
      s !== void 0 && (e[o] = Ie(s));
  else n !== void 0 && (e[t] = Ie(n));
}, Re = (e = 0, t = 0, n = 0, o = 0) => {
  const s = { x: e, y: t, width: n, height: o, top: t, left: e, right: e + n, bottom: t + o };
  return { ...s, toJSON: () => JSON.stringify(s) };
}, to = (e) => {
  let t, n = -1, o = !1;
  return {
    next: (...s) => {
      t = s, o || (o = !0, n = requestAnimationFrame(() => {
        e(...t), o = !1;
      }));
    },
    cancel: () => {
      cancelAnimationFrame(n), o = !1;
    }
  };
}, Be = (e, t, n = "touch") => {
  switch (n) {
    case "center": {
      const o = t.left + t.width / 2, s = t.top + t.height / 2;
      return o >= e.left && o <= e.right && s >= e.top && s <= e.bottom;
    }
    case "cover":
      return t.left >= e.left && t.top >= e.top && t.right <= e.right && t.bottom <= e.bottom;
    case "touch":
      return e.right >= t.left && e.left <= t.right && e.bottom >= t.top && e.top <= t.bottom;
  }
}, no = () => matchMedia("(hover: none), (pointer: coarse)").matches, oo = () => "safari" in window, he = (e) => Array.isArray(e) ? e : [e], ct = (e) => (t, n, o, s = {}) => {
  (t instanceof HTMLCollection || t instanceof NodeList) && (t = Array.from(t)), n = he(n), t = he(t);
  for (const i of t)
    if (i)
      for (const l of n)
        i[e](l, o, { capture: !1, ...s });
}, W = ct("addEventListener"), O = ct("removeEventListener"), J = (e) => {
  const { clientX: t, clientY: n, target: o } = e.touches?.[0] ?? e;
  return { x: t, y: n, target: o };
}, Y = (e, t = document) => he(e).map((n) => typeof n == "string" ? Array.from(t.querySelectorAll(n)) : n instanceof Element ? n : null).flat().filter(Boolean), so = (e, t) => t.some((n) => typeof n == "number" ? e.button === n : typeof n == "object" ? n.button !== e.button ? !1 : n.modifiers.every((o) => {
  switch (o) {
    case "alt":
      return e.altKey;
    case "ctrl":
      return e.ctrlKey || e.metaKey;
    case "shift":
      return e.shiftKey;
  }
}) : !1), { abs: j, max: We, min: Ye, ceil: Xe } = Math, Fe = (e = []) => ({
  stored: e,
  selected: [],
  touched: [],
  changed: { added: [], removed: [] }
});
class io extends eo {
  static version = "mind-elixir-fork";
  // Options
  _options;
  // Selection store
  _selection = Fe();
  // Area element and clipping element
  _area;
  _clippingElement;
  // Target container (element) and boundary (cached)
  _targetElement;
  _targetBoundary;
  _targetBoundaryScrolled = !0;
  _targetRect;
  _selectables = [];
  _latestElement;
  // Dynamically constructed area rect
  _areaLocation = { y1: 0, x2: 0, y2: 0, x1: 0 };
  _areaRect = Re();
  // If a single click is being performed, it's a single-click until the user dragged the mouse
  _singleClick = !0;
  _frame;
  // Required data for scrolling
  _scrollAvailable = !0;
  _scrollingActive = !1;
  _scrollSpeed = { x: 0, y: 0 };
  _scrollDelta = { x: 0, y: 0 };
  constructor(t) {
    super(), this._options = {
      selectionAreaClass: "selection-area",
      selectionContainerClass: void 0,
      selectables: [],
      document: window.document,
      startAreas: ["html"],
      boundaries: ["html"],
      container: "body",
      mindElixirInstance: void 0,
      // 添加默认值
      ...t,
      behaviour: {
        overlap: "invert",
        intersect: "touch",
        triggers: [0],
        ...t.behaviour,
        startThreshold: t.behaviour?.startThreshold ? typeof t.behaviour.startThreshold == "number" ? t.behaviour.startThreshold : { x: 10, y: 10, ...t.behaviour.startThreshold } : { x: 10, y: 10 },
        scrolling: {
          speedDivider: 10,
          ...t.behaviour?.scrolling,
          startScrollMargins: {
            x: 0,
            y: 0,
            ...t.behaviour?.scrolling?.startScrollMargins
          }
        }
      },
      features: {
        range: !0,
        touch: !0,
        deselectOnBlur: !1,
        ...t.features,
        singleTap: {
          allow: !0,
          intersect: "native",
          ...t.features?.singleTap
        }
      }
    };
    for (const i of Object.getOwnPropertyNames(Object.getPrototypeOf(this)))
      typeof this[i] == "function" && (this[i] = this[i].bind(this));
    const { document: n, selectionAreaClass: o, selectionContainerClass: s } = this._options;
    this._area = n.createElement("div"), this._clippingElement = n.createElement("div"), this._clippingElement.appendChild(this._area), this._area.classList.add(o), s && this._clippingElement.classList.add(s), $(this._area, {
      willChange: "top, left, bottom, right, width, height",
      top: 0,
      left: 0,
      position: "fixed"
    }), $(this._clippingElement, {
      overflow: "hidden",
      position: "fixed",
      transform: "translate3d(0, 0, 0)",
      // https://stackoverflow.com/a/38268846
      pointerEvents: "none",
      zIndex: "1"
    }), this._frame = to((i) => {
      this._recalculateSelectionAreaRect(), this._updateElementSelection(), this._emitEvent("move", i), this._redrawSelectionArea();
    }), this.enable();
  }
  _toggleStartEvents(t = !0) {
    const { document: n } = this._options;
    (t ? W : O)(n, "pointerdown", this._onTapStart);
  }
  _onTapStart(t, n = !1) {
    const { x: o, y: s, target: i } = J(t), { document: l, startAreas: c, boundaries: r, behaviour: a, features: d } = this._options, h = i.getBoundingClientRect();
    if (!so(t, a.triggers))
      return;
    const u = Y(c, l), b = Y(r, l);
    this._targetElement = b.find((m) => Be(m.getBoundingClientRect(), h));
    const v = t.composedPath(), p = u.find((m) => v.includes(m));
    if (this._targetBoundary = b.find((m) => v.includes(m)), !this._targetElement || !p || !this._targetBoundary || !n && this._emitEvent("beforestart", t) === !1)
      return;
    this._areaLocation = { x1: o, y1: s, x2: 0, y2: 0 };
    const g = l.scrollingElement ?? l.body;
    this._scrollDelta = { x: g.scrollLeft, y: g.scrollTop }, this._singleClick = !0, this.clearSelection(!1, !0), W(l, ["pointermove"], this._delayedTapMove, { passive: !1 }), W(l, ["pointerup", "pointercancel"], this._onTapStop), W(l, "scroll", this._onScroll), d.deselectOnBlur && (this._targetBoundaryScrolled = !1, W(this._targetBoundary, "scroll", this._onStartAreaScroll));
  }
  _onSingleTap(t) {
    const {
      singleTap: { intersect: n },
      range: o
    } = this._options.features, s = J(t);
    let i;
    if (n === "native")
      i = s.target;
    else if (n === "touch") {
      this.resolveSelectables();
      const { x: c, y: r } = s;
      i = this._selectables.find((a) => {
        const { right: d, left: h, top: u, bottom: b } = a.getBoundingClientRect();
        return c < d && c > h && r < b && r > u;
      });
    }
    if (!i)
      return;
    for (this.resolveSelectables(); !this._selectables.includes(i); )
      if (i.parentElement)
        i = i.parentElement;
      else {
        this._targetBoundaryScrolled || this.clearSelection();
        return;
      }
    const { stored: l } = this._selection;
    if (this._emitEvent("start", t), t.shiftKey && o && this._latestElement) {
      const c = this._latestElement, [r, a] = c.compareDocumentPosition(i) & 4 ? [i, c] : [c, i], d = [
        ...this._selectables.filter((h) => h.compareDocumentPosition(r) & 4 && h.compareDocumentPosition(a) & 2),
        r,
        a
      ];
      this.select(d), this._latestElement = c;
    } else l.includes(i) && (l.length === 1 || t.ctrlKey || l.every((c) => this._selection.stored.includes(c))) ? this.deselect(i) : (this.select(i), this._latestElement = i);
  }
  _delayedTapMove(t) {
    const {
      container: n,
      document: o,
      behaviour: { startThreshold: s }
    } = this._options, { x1: i, y1: l } = this._areaLocation, { x: c, y: r } = J(t);
    if (
      // Single number for both coordinates
      typeof s == "number" && j(c + r - (i + l)) >= s || // Different x and y threshold
      typeof s == "object" && j(c - i) >= s.x || j(r - l) >= s.y
    ) {
      if (O(o, ["pointermove"], this._delayedTapMove, { passive: !1 }), this._emitEvent("beforedrag", t) === !1) {
        O(o, ["pointerup", "pointercancel"], this._onTapStop);
        return;
      }
      W(o, ["pointermove"], this._onTapMove, { passive: !1 }), $(this._area, "display", "block"), Y(n, o)[0].appendChild(this._clippingElement), this.resolveSelectables(), this._singleClick = !1, this._targetRect = this._targetElement.getBoundingClientRect(), this._scrollAvailable = this._targetElement.scrollHeight !== this._targetElement.clientHeight || this._targetElement.scrollWidth !== this._targetElement.clientWidth, this._scrollAvailable && (this._selectables = this._selectables.filter((a) => this._targetElement.contains(a))), this._setupSelectionArea(), this._emitEvent("start", t), this._onTapMove(t);
    }
    this._handleMoveEvent(t);
  }
  _setupSelectionArea() {
    const { _clippingElement: t, _targetElement: n, _area: o } = this, s = this._targetRect = n.getBoundingClientRect();
    this._scrollAvailable ? ($(t, {
      top: s.top,
      left: s.left,
      width: s.width,
      height: s.height
    }), $(o, {
      marginTop: -s.top,
      marginLeft: -s.left
    })) : ($(t, {
      top: 0,
      left: 0,
      width: "100%",
      height: "100%"
    }), $(o, {
      marginTop: 0,
      marginLeft: 0
    }));
  }
  _onTapMove(t) {
    const { _scrollSpeed: n, _areaLocation: o, _options: s, _frame: i } = this, { speedDivider: l } = s.behaviour.scrolling, { x: c, y: r } = J(t);
    if (o.x2 = c, o.y2 = r, this._scrollAvailable && !this._scrollingActive && (n.y || n.x)) {
      this._scrollingActive = !0;
      const a = () => {
        if (!n.x && !n.y) {
          this._scrollingActive = !1;
          return;
        }
        const d = this._options.mindElixirInstance;
        if (d && d.move) {
          const h = n.x ? Xe(n.x / l) : 0, u = n.y ? Xe(n.y / l) : 0;
          (h || u) && (d.move(-h, -u), o.x1 -= h, o.y1 -= u);
        }
        i.next(t), requestAnimationFrame(a);
      };
      requestAnimationFrame(a);
    } else
      i.next(t);
    this._handleMoveEvent(t);
  }
  _handleMoveEvent(t) {
    const { features: n } = this._options;
    (n.touch && no() || this._scrollAvailable && oo()) && t.preventDefault();
  }
  _onScroll() {
    const {
      _scrollDelta: t,
      _options: { document: n }
    } = this, { scrollTop: o, scrollLeft: s } = n.scrollingElement ?? n.body;
    this._areaLocation.x1 += t.x - s, this._areaLocation.y1 += t.y - o, t.x = s, t.y = o, this._setupSelectionArea(), this._frame.next(null);
  }
  _onStartAreaScroll() {
    this._targetBoundaryScrolled = !0, O(this._targetElement, "scroll", this._onStartAreaScroll);
  }
  _recalculateSelectionAreaRect() {
    const { _scrollSpeed: t, _areaLocation: n, _targetElement: o, _options: s } = this, i = this._targetRect, { x1: l, y1: c } = n;
    let { x2: r, y2: a } = n;
    const {
      behaviour: {
        scrolling: { startScrollMargins: d }
      }
    } = s;
    r < i.left + d.x ? (t.x = -j(i.left - r + d.x), r = r < i.left ? i.left : r) : r > i.right - d.x ? (t.x = j(i.left + i.width - r - d.x), r = r > i.right ? i.right : r) : t.x = 0, a < i.top + d.y ? (t.y = -j(i.top - a + d.y), a = a < i.top ? i.top : a) : a > i.bottom - d.y ? (t.y = j(i.top + i.height - a - d.y), a = a > i.bottom ? i.bottom : a) : t.y = 0;
    const h = Ye(l, r), u = Ye(c, a), b = We(l, r), v = We(c, a);
    this._areaRect = Re(h, u, b - h, v - u);
  }
  _redrawSelectionArea() {
    const { x: t, y: n, width: o, height: s } = this._areaRect, { style: i } = this._area;
    i.left = `${t}px`, i.top = `${n}px`, i.width = `${o}px`, i.height = `${s}px`;
  }
  _onTapStop(t, n) {
    const { document: o, features: s } = this._options, { _singleClick: i } = this;
    O(this._targetElement, "scroll", this._onStartAreaScroll), O(o, ["pointermove"], this._delayedTapMove), O(o, ["pointermove"], this._onTapMove), O(o, ["pointerup", "pointercancel"], this._onTapStop), O(o, "scroll", this._onScroll), this._keepSelection(), t && i && s.singleTap.allow ? this._onSingleTap(t) : !i && !n && (this._updateElementSelection(), this._emitEvent("stop", t)), this._scrollSpeed.x = 0, this._scrollSpeed.y = 0, this._clippingElement.remove(), this._frame?.cancel(), $(this._area, "display", "none");
  }
  _updateElementSelection() {
    const { _selectables: t, _options: n, _selection: o, _areaRect: s } = this, { stored: i, selected: l, touched: c } = o, { intersect: r, overlap: a } = n.behaviour, d = a === "invert", h = [], u = [], b = [];
    for (let p = 0; p < t.length; p++) {
      const g = t[p];
      if (Be(s, g.getBoundingClientRect(), r)) {
        if (l.includes(g))
          i.includes(g) && !c.includes(g) && c.push(g);
        else if (d && i.includes(g)) {
          b.push(g);
          continue;
        } else
          u.push(g);
        h.push(g);
      }
    }
    d && u.push(...i.filter((p) => !l.includes(p)));
    const v = a === "keep";
    for (let p = 0; p < l.length; p++) {
      const g = l[p];
      !h.includes(g) && !// Check if the user wants to keep previously selected elements, e.g.,
      // not make them part of the current selection as soon as they're touched.
      (v && i.includes(g)) && b.push(g);
    }
    o.selected = h, o.changed = { added: u, removed: b }, this._latestElement = void 0;
  }
  _emitEvent(t, n) {
    return this.emit(t, {
      event: n,
      store: this._selection,
      selection: this
    });
  }
  _keepSelection() {
    const { _options: t, _selection: n } = this, { selected: o, changed: s, touched: i, stored: l } = n, c = o.filter((r) => !l.includes(r));
    switch (t.behaviour.overlap) {
      case "drop": {
        n.stored = [
          ...c,
          ...l.filter((r) => !i.includes(r))
          // Elements not touched
        ];
        break;
      }
      case "invert": {
        n.stored = [
          ...c,
          ...l.filter((r) => !s.removed.includes(r))
          // Elements not removed from selection
        ];
        break;
      }
      case "keep": {
        n.stored = [
          ...l,
          ...o.filter((r) => !l.includes(r))
          // Newly added
        ];
        break;
      }
    }
  }
  /**
   * Manually triggers the start of a selection
   * @param evt A PointerEvent-like object
   * @param silent If beforestart should be fired
   */
  trigger(t, n = !0) {
    this._onTapStart(t, n);
  }
  /**
   * Can be used if during a selection elements have been added
   * Will update everything that can be selected
   */
  resolveSelectables() {
    this._selectables = Y(this._options.selectables, this._options.document);
  }
  /**
   * Same as deselecting, but for all elements currently selected
   * @param includeStored If the store should also get cleared
   * @param quiet If move / stop events should be fired
   */
  clearSelection(t = !0, n = !1) {
    const { selected: o, stored: s, changed: i } = this._selection;
    i.added = [], i.removed.push(...o, ...t ? s : []), n || (this._emitEvent("move", null), this._emitEvent("stop", null)), this._selection = Fe(t ? [] : s);
  }
  /**
   * @returns {Array} Selected elements
   */
  getSelection() {
    return this._selection.stored;
  }
  /**
   * @returns {HTMLElement} The selection area element
   */
  getSelectionArea() {
    return this._area;
  }
  /**
   * @returns {Element[]} Available selectable elements for current selection
   */
  getSelectables() {
    return this._selectables;
  }
  /**
   * Set the location of the selection area
   * @param location A partial AreaLocation object
   */
  setAreaLocation(t) {
    Object.assign(this._areaLocation, t), this._redrawSelectionArea();
  }
  /**
   * @returns {AreaLocation} The current location of the selection area
   */
  getAreaLocation() {
    return this._areaLocation;
  }
  /**
   * Cancel the current selection process, pass true to fire a stop event after cancel
   * @param keepEvent If a stop event should be fired
   */
  cancel(t = !1) {
    this._onTapStop(null, !t);
  }
  /**
   * Unbinds all events and removes the area-element.
   */
  destroy() {
    this.cancel(), this.disable(), this._clippingElement.remove(), super.unbindAllListeners();
  }
  /**
   * Enable selecting elements
   */
  enable = this._toggleStartEvents;
  /**
   * Disable selecting elements
   */
  disable = this._toggleStartEvents.bind(this, !1);
  /**
   * Adds elements to the selection
   * @param query CSS Query, can be an array of queries
   * @param quiet If this should not trigger the move event
   */
  select(t, n = !1) {
    const { changed: o, selected: s, stored: i } = this._selection, l = Y(t, this._options.document).filter((c) => !s.includes(c) && !i.includes(c));
    return i.push(...l), s.push(...l), o.added.push(...l), o.removed = [], this._latestElement = void 0, n || (this._emitEvent("move", null), this._emitEvent("stop", null)), l;
  }
  /**
   * Removes a particular element from the selection
   * @param query CSS Query, can be an array of queries
   * @param quiet If this should not trigger the move event
   */
  deselect(t, n = !1) {
    const { selected: o, stored: s, changed: i } = this._selection, l = Y(t, this._options.document).filter((c) => o.includes(c) || s.includes(c));
    this._selection.stored = s.filter((c) => !l.includes(c)), this._selection.selected = o.filter((c) => !l.includes(c)), this._selection.changed.added = [], this._selection.changed.removed.push(...l.filter((c) => !i.removed.includes(c))), this._latestElement = void 0, n || (this._emitEvent("move", null), this._emitEvent("stop", null));
  }
}
function ro(e) {
  const t = e.mouseSelectionButton === 2 ? [2] : [0], n = new io({
    selectables: [".map-container me-tpc"],
    boundaries: [e.container],
    container: e.selectionContainer,
    mindElixirInstance: e,
    // 传递 MindElixir 实例
    features: {
      touch: !1,
      singleTap: {
        allow: !1
      }
    },
    behaviour: {
      triggers: t,
      // Scroll configuration.
      scrolling: {
        // On scrollable areas the number on px per frame is devided by this amount.
        // Default is 10 to provide a enjoyable scroll experience.
        speedDivider: 10,
        startScrollMargins: { x: 50, y: 50 }
      }
    }
  }).on("beforestart", ({ event: o }) => {
    if (!e.editable || e.spacePressed || e.ptState !== 5) return !1;
    const s = o.target;
    if (s.id === "input-box" || s.className === "circle" || s.className !== "map-container")
      return !1;
    !o.ctrlKey && !o.metaKey && e.clearSelection();
    const i = n.getSelectionArea();
    return i.style.background = "#4f90f22d", i.style.border = "1px solid #4f90f2", i.style.borderRadius = "3px", i.parentElement && (i.parentElement.style.zIndex = "9999"), !0;
  }).on(
    "move",
    ({
      store: {
        changed: { added: o, removed: s }
      }
    }) => {
      if (o.length > 0 || s.length > 0, o.length > 0) {
        const i = o.filter((l) => !e.currentNodes?.includes(l));
        if (i.length > 0) {
          for (const l of i)
            l.className = "selected";
          e.currentNodes = [...e.currentNodes || [], ...i], e.bus.fire(
            "selectNodes",
            i.map((l) => l.nodeObj)
          );
        }
      }
      if (s.length > 0) {
        const i = s.filter((l) => e.currentNodes?.includes(l));
        if (i.length > 0) {
          for (const l of i)
            l.classList.remove("selected");
          e.currentNodes = (e.currentNodes || []).filter((l) => !i.includes(l)), e.bus.fire(
            "unselectNodes",
            i.map((l) => l.nodeObj)
          );
        }
      }
    }
  );
  e.selection = n;
}
function at({ pT: e, pL: t, pW: n, pH: o, cT: s, cL: i, cW: l, cH: c, direction: r, containerHeight: a }) {
  let d = t + n / 2;
  const h = e + o / 2;
  let u;
  r === H.LHS ? u = i + l : u = i;
  const b = s + c / 2, p = (1 - Math.abs(b - h) / a) * 0.25 * (n / 2);
  return r === H.LHS ? d = d - n / 10 - p : d = d + n / 10 + p, `M ${d} ${h} Q ${d} ${b} ${u} ${b}`;
}
function dt({ pT: e, pL: t, pW: n, pH: o, cT: s, cL: i, cW: l, cH: c, direction: r, isFirst: a }) {
  const d = parseInt(this.container.style.getPropertyValue("--node-gap-x"));
  let h = 0, u = 0;
  a ? h = e + o / 2 : h = e + o;
  const b = s + c;
  let v = 0, p = 0, g = 0;
  const m = Math.abs(h - b) / 300 * d;
  return r === H.LHS ? (g = t, v = g + d, p = g - d, u = i + d, `M ${v} ${h} C ${g} ${h} ${g + m} ${b} ${p} ${b} H ${u}`) : (g = t + n, v = g - d, p = g + d, u = i + l - d, `M ${v} ${h} C ${g} ${h} ${g - m} ${b} ${p} ${b} H ${u}`);
}
const lo = function(e, t = !0) {
  this.theme = e, this.generateMainBranch = this.theme.generateMainBranch || at, this.generateSubBranch = this.theme.generateSubBranch || dt;
  const o = {
    ...(this.theme.type === "dark" ? ue : fe).cssVar,
    ...this.theme.cssVar
  };
  this.compact && (o["--node-gap-x"] = "15px", o["--node-gap-y"] = "2px", o["--main-gap-x"] = "30px", o["--main-gap-y"] = "6px");
  const s = Object.keys(o);
  for (let i = 0; i < s.length; i++) {
    const l = s[i];
    this.container.style.setProperty(l, o[l]);
  }
  t && this.refresh();
}, co = function(e) {
  this.compact = e, this.theme && this.changeTheme(this.theme);
}, ao = function(e) {
  return {
    dom: e,
    moved: !1,
    // differentiate click and move
    pointerdown: !1,
    lastX: 0,
    lastY: 0,
    handlePointerMove(t) {
      if (this.pointerdown) {
        this.moved = !0;
        const n = t.clientX - this.lastX, o = t.clientY - this.lastY;
        this.lastX = t.clientX, this.lastY = t.clientY, this.cb && this.cb(n, o);
      }
    },
    handlePointerDown(t) {
      t.button === 0 && (this.pointerdown = !0, this.lastX = t.clientX, this.lastY = t.clientY, this.dom.setPointerCapture(t.pointerId));
    },
    handleClear(t) {
      this.pointerdown = !1, t.pointerId !== void 0 && this.dom.releasePointerCapture(t.pointerId);
    },
    cb: null,
    init(t, n) {
      this.cb = n, this.handleClear = this.handleClear.bind(this), this.handlePointerMove = this.handlePointerMove.bind(this), this.handlePointerDown = this.handlePointerDown.bind(this), this.destroy = qe([
        { dom: t, evt: "pointermove", func: this.handlePointerMove },
        { dom: t, evt: "pointerleave", func: this.handleClear },
        { dom: t, evt: "pointerup", func: this.handleClear },
        { dom: this.dom, evt: "pointerdown", func: this.handlePointerDown }
      ]);
    },
    destroy: null,
    clear() {
      this.moved = !1, this.pointerdown = !1;
    }
  };
}, Ke = {
  create: ao
}, ht = "#4dc4ff";
function ft(e, t, n, o, s, i, l, c) {
  return {
    x: e / 8 + n * 3 / 8 + s * 3 / 8 + l / 8,
    y: t / 8 + o * 3 / 8 + i * 3 / 8 + c / 8
  };
}
function ho(e, t, n) {
  e && (e.dataset.x = t.toString(), e.dataset.y = n.toString(), re(e));
}
function Z(e, t, n, o, s) {
  k(e, {
    x1: t + "",
    y1: n + "",
    x2: o + "",
    y2: s + ""
  });
}
function Ve(e, t, n, o, s, i, l, c, r, a) {
  const d = `M ${t} ${n} C ${o} ${s} ${i} ${l} ${c} ${r}`;
  if (e.line.setAttribute("d", d), a.style) {
    const p = a.style;
    p.stroke && e.line.setAttribute("stroke", p.stroke), p.strokeWidth && e.line.setAttribute("stroke-width", String(p.strokeWidth)), p.strokeDasharray && e.line.setAttribute("stroke-dasharray", p.strokeDasharray), p.strokeLinecap && e.line.setAttribute("stroke-linecap", p.strokeLinecap), p.opacity !== void 0 && e.line.setAttribute("opacity", String(p.opacity));
  }
  const h = e.querySelectorAll('path[stroke="transparent"]');
  h.length > 0 && h[0].setAttribute("d", d);
  const u = oe(i, l, c, r);
  if (u) {
    const p = `M ${u.x1} ${u.y1} L ${c} ${r} L ${u.x2} ${u.y2}`;
    if (e.arrow1.setAttribute("d", p), h.length > 1 && h[1].setAttribute("d", p), a.style) {
      const g = a.style;
      g.stroke && e.arrow1.setAttribute("stroke", g.stroke), g.strokeWidth && e.arrow1.setAttribute("stroke-width", String(g.strokeWidth)), g.strokeLinecap && e.arrow1.setAttribute("stroke-linecap", g.strokeLinecap), g.opacity !== void 0 && e.arrow1.setAttribute("opacity", String(g.opacity));
    }
  }
  if (a.bidirectional) {
    const p = oe(o, s, t, n);
    if (p) {
      const g = `M ${p.x1} ${p.y1} L ${t} ${n} L ${p.x2} ${p.y2}`;
      if (e.arrow2.setAttribute("d", g), h.length > 2 && h[2].setAttribute("d", g), a.style) {
        const m = a.style;
        m.stroke && e.arrow2.setAttribute("stroke", m.stroke), m.strokeWidth && e.arrow2.setAttribute("stroke-width", String(m.strokeWidth)), m.strokeLinecap && e.arrow2.setAttribute("stroke-linecap", m.strokeLinecap), m.opacity !== void 0 && e.arrow2.setAttribute("opacity", String(m.opacity));
      }
    }
  }
  const { x: b, y: v } = ft(t, n, o, s, i, l, c, r);
  if (e.labelEl && ho(e.labelEl, b, v), a.style?.labelColor) {
    const p = e.labelEl;
    p && (p.style.color = a.style.labelColor);
  }
  vo(e);
}
function se(e, t, n) {
  const { offsetLeft: o, offsetTop: s } = M(e.nodes, t), i = t.offsetWidth, l = t.offsetHeight, c = o + i / 2, r = s + l / 2, a = c + n.x, d = r + n.y;
  return {
    w: i,
    h: l,
    cx: c,
    cy: r,
    ctrlX: a,
    ctrlY: d
  };
}
function X(e) {
  let t, n;
  const o = (e.cy - e.ctrlY) / (e.ctrlX - e.cx);
  return o > e.h / e.w || o < -e.h / e.w ? e.cy - e.ctrlY < 0 ? (t = e.cx - e.h / 2 / o, n = e.cy + e.h / 2) : (t = e.cx + e.h / 2 / o, n = e.cy - e.h / 2) : e.cx - e.ctrlX < 0 ? (t = e.cx + e.w / 2, n = e.cy - e.w * o / 2) : (t = e.cx - e.w / 2, n = e.cy + e.w * o / 2), {
    x: t,
    y: n
  };
}
const fo = function(e, t, n) {
  const o = M(e.nodes, t), s = M(e.nodes, n), i = o.offsetLeft + t.offsetWidth / 2, l = o.offsetTop + t.offsetHeight / 2, c = s.offsetLeft + n.offsetWidth / 2, r = s.offsetTop + n.offsetHeight / 2, a = c - i, d = r - l, h = Math.sqrt(a * a + d * d), u = Math.max(50, Math.min(200, h * 0.3)), b = Math.abs(a), v = Math.abs(d);
  let p, g;
  if (h < 150) {
    const w = t.closest("me-main").className === "lhs" ? -1 : 1;
    p = { x: 200 * w, y: 0 }, g = { x: 200 * w, y: 0 };
  } else if (b > v * 1.5) {
    const w = a > 0 ? t.offsetWidth / 2 : -t.offsetWidth / 2, E = a > 0 ? -n.offsetWidth / 2 : n.offsetWidth / 2;
    p = { x: w + (a > 0 ? u : -u), y: 0 }, g = { x: E + (a > 0 ? -u : u), y: 0 };
  } else if (v > b * 1.5) {
    const w = d > 0 ? t.offsetHeight / 2 : -t.offsetHeight / 2, E = d > 0 ? -n.offsetHeight / 2 : n.offsetHeight / 2;
    p = { x: 0, y: w + (d > 0 ? u : -u) }, g = { x: 0, y: E + (d > 0 ? -u : u) };
  } else {
    const w = Math.atan2(d, a), E = t.offsetWidth / 2 * Math.cos(w), N = t.offsetHeight / 2 * Math.sin(w), f = -(n.offsetWidth / 2) * Math.cos(w), y = -(n.offsetHeight / 2) * Math.sin(w), x = u * 0.7 * (a > 0 ? 1 : -1), S = u * 0.7 * (d > 0 ? 1 : -1);
    p = { x: E + x, y: N + S }, g = { x: f - x, y: y - S };
  }
  return {
    delta1: { x: Math.round(p.x), y: Math.round(p.y) },
    delta2: { x: Math.round(g.x), y: Math.round(g.y) }
  };
}, Se = function(e, t, n, o, s) {
  if (!t || !n)
    return;
  if (!o.delta1 || !o.delta2) {
    const C = fo(e, t, n);
    o.delta1 = C.delta1, o.delta2 = C.delta2;
  }
  const i = se(e, t, o.delta1), l = se(e, n, o.delta2), { x: c, y: r } = X(i), { ctrlX: a, ctrlY: d } = i, { ctrlX: h, ctrlY: u } = l, { x: b, y: v } = X(l), p = oe(h, u, b, v);
  if (!p) return;
  const g = `M ${p.x1} ${p.y1} L ${b} ${v} L ${p.x2} ${p.y2}`;
  let m = "";
  if (o.bidirectional) {
    const C = oe(a, d, c, r);
    if (!C) return;
    m = `M ${C.x1} ${C.y1} L ${c} ${r} L ${C.x2} ${C.y2}`;
  }
  const w = jn(`M ${c} ${r} C ${a} ${d} ${h} ${u} ${b} ${v}`, g, m, o.style), { x: E, y: N } = ft(c, r, a, d, h, u, b, v), f = o.style?.labelColor || "rgb(235, 95, 82)", y = "a-" + o.id;
  w.id = y;
  const x = e.markdown ? e.markdown(o.label, o) : o.label, S = de(x, E, N, {
    anchor: "middle",
    color: f,
    dataType: "arrow",
    svgId: y
  });
  w.labelEl = S, w.arrowObj = o, w.dataset.linkid = o.id, e.labelContainer.appendChild(S), e.arrowSvg.appendChild(w), re(S), s || (e.arrows.push(o), e.currentArrow = w, pt(e, o, i, l));
}, uo = function(e, t, n = {}) {
  const o = {
    id: B(),
    label: "Custom Link",
    from: e.nodeObj.id,
    to: t.nodeObj.id,
    ...n
  };
  Se(this, e, t, o), this.bus.fire("operation", {
    name: "createArrow",
    obj: o
  });
}, po = function(e) {
  le(this);
  const t = { ...e, id: B() };
  Se(this, this.findEle(t.from), this.findEle(t.to), t), this.bus.fire("operation", {
    name: "createArrow",
    obj: t
  });
}, go = function(e) {
  let t;
  if (e ? t = e : t = this.currentArrow, !t) return;
  le(this);
  const n = t.arrowObj.id;
  this.arrows = this.arrows.filter((o) => o.id !== n), t.labelEl?.remove(), t.remove(), this.bus.fire("operation", {
    name: "removeArrow",
    obj: {
      id: n
    }
  });
}, mo = function(e) {
  this.currentArrow = e;
  const t = e.arrowObj, n = this.findEle(t.from), o = this.findEle(t.to), s = se(this, n, t.delta1), i = se(this, o, t.delta2);
  this.editable ? pt(this, t, s, i) : ut(e, ht), this.bus.fire("selectArrow", t);
}, yo = function() {
  le(this), this.currentArrow = null, this.bus.fire("unselectArrow");
}, ce = function(e, t) {
  const n = document.createElementNS(A, "path");
  return k(n, {
    d: e,
    stroke: t,
    fill: "none",
    "stroke-width": "6",
    "stroke-linecap": "round",
    "stroke-linejoin": "round"
  }), n;
}, ut = function(e, t) {
  const n = document.createElementNS(A, "g");
  n.setAttribute("class", "arrow-highlight"), n.setAttribute("opacity", "0.45");
  const o = ce(e.line.getAttribute("d"), t);
  n.appendChild(o);
  const s = ce(e.arrow1.getAttribute("d"), t);
  if (n.appendChild(s), e.arrow2.getAttribute("d")) {
    const i = ce(e.arrow2.getAttribute("d"), t);
    n.appendChild(i);
  }
  e.insertBefore(n, e.firstChild);
}, bo = function(e) {
  const t = e.querySelector(".arrow-highlight");
  t && t.remove();
}, vo = function(e) {
  const t = e.querySelector(".arrow-highlight");
  if (!t) return;
  const n = t.querySelectorAll("path");
  n.length >= 1 && n[0].setAttribute("d", e.line.getAttribute("d")), n.length >= 2 && n[1].setAttribute("d", e.arrow1.getAttribute("d")), n.length >= 3 && e.arrow2.getAttribute("d") && n[2].setAttribute("d", e.arrow2.getAttribute("d"));
}, le = function(e) {
  e.helper1?.destroy(), e.helper2?.destroy(), e.linkController.style.display = "none", e.P2.style.display = "none", e.P3.style.display = "none", e.currentArrow && bo(e.currentArrow);
}, pt = function(e, t, n, o) {
  const { linkController: s, P2: i, P3: l, line1: c, line2: r, nodes: a, map: d, currentArrow: h, bus: u } = e;
  if (!h) return;
  s.style.display = "initial", i.style.display = "initial", l.style.display = "initial", a.appendChild(s), a.appendChild(i), a.appendChild(l), ut(h, ht);
  let { x: b, y: v } = X(n), { ctrlX: p, ctrlY: g } = n, { ctrlX: m, ctrlY: w } = o, { x: E, y: N } = X(o);
  i.style.cssText = `top:${g}px;left:${p}px;`, l.style.cssText = `top:${w}px;left:${m}px;`, Z(c, b, v, p, g), Z(r, m, w, E, N), e.helper1 = Ke.create(i), e.helper2 = Ke.create(l), e.helper1.init(d, (f, y) => {
    p = p + f / e.scaleVal, g = g + y / e.scaleVal;
    const x = X({ ...n, ctrlX: p, ctrlY: g });
    b = x.x, v = x.y, i.style.top = g + "px", i.style.left = p + "px", Ve(h, b, v, p, g, m, w, E, N, t), Z(c, b, v, p, g), t.delta1.x = Math.round(p - n.cx), t.delta1.y = Math.round(g - n.cy), u.fire("updateArrowDelta", t);
  }), e.helper2.init(d, (f, y) => {
    m = m + f / e.scaleVal, w = w + y / e.scaleVal;
    const x = X({ ...o, ctrlX: m, ctrlY: w });
    E = x.x, N = x.y, l.style.top = w + "px", l.style.left = m + "px", Ve(h, b, v, p, g, m, w, E, N, t), Z(r, m, w, E, N), t.delta2.x = Math.round(m - o.cx), t.delta2.y = Math.round(w - o.cy), u.fire("updateArrowDelta", t);
  });
};
function wo() {
  this.arrowSvg.innerHTML = "", this.labelContainer.querySelectorAll('.svg-label[data-type="arrow"]').forEach((t) => t.remove());
  for (let t = 0; t < this.arrows.length; t++) {
    const n = this.arrows[t];
    try {
      Se(this, this.findEle(n.from), this.findEle(n.to), n, !0);
    } catch {
    }
  }
  this.nodes.appendChild(this.arrowSvg);
}
function xo(e) {
  le(this), e && e.labelEl && rt(this, e.labelEl, e.arrowObj);
}
function Eo() {
  this.arrows = this.arrows.filter((e) => ne(e.from, this.nodeData) && ne(e.to, this.nodeData));
}
const Co = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  createArrow: uo,
  createArrowFrom: po,
  editArrowLabel: xo,
  removeArrow: go,
  renderArrow: wo,
  selectArrow: mo,
  tidyArrow: Eo,
  unselectArrow: yo
}, Symbol.toStringTag, { value: "Module" })), So = function(e) {
  if (e.length === 0) throw new Error("No selected node.");
  if (e.length === 1) {
    const r = e[0].nodeObj, a = e[0].nodeObj.parent;
    if (!a) throw new Error("Can not select root node.");
    const d = a.children.findIndex((h) => r === h);
    return {
      parent: a.id,
      start: d,
      end: d
    };
  }
  let t = 0;
  const n = e.map((r) => {
    let a = r.nodeObj;
    const d = [];
    for (; a.parent; ) {
      const h = a.parent, b = h.children?.indexOf(a);
      a = h, d.unshift({ node: a, index: b });
    }
    return d.length > t && (t = d.length), d;
  });
  let o = 0;
  e: for (; o < t; o++) {
    const r = n[0][o]?.node;
    for (let a = 1; a < n.length; a++)
      if (n[a][o]?.node !== r)
        break e;
  }
  if (!o) throw new Error("Can not select root node.");
  const s = n.map((r) => r[o - 1].index).sort(), i = s[0] || 0, l = s[s.length - 1] || 0, c = n[0][o - 1].node;
  if (!c.parent) throw new Error("Please select nodes in the same main topic.");
  return {
    parent: c.id,
    start: i,
    end: l
  };
}, No = function(e) {
  const t = document.createElementNS(A, "g");
  return t.setAttribute("id", e), t;
}, ze = function(e, t) {
  const n = document.createElementNS(A, "path");
  return k(n, {
    d: e,
    stroke: t || "#666",
    fill: "none",
    "stroke-linecap": "round",
    "stroke-width": "2"
  }), n;
}, To = (e) => e.parentElement.parentElement, ko = function(e, { parent: t, start: n }) {
  const o = e.findEle(t), s = o.nodeObj;
  let i;
  return s.parent ? i = o.closest("me-main").className : i = e.findEle(s.children[n].id).closest("me-main").className, i;
}, Ne = function(e, t) {
  const { id: n, label: o, parent: s, start: i, end: l, style: c } = t, { nodes: r, theme: a, summarySvg: d } = e, u = e.findEle(s).nodeObj, b = ko(e, t);
  let v = 1 / 0, p = 0, g = 0, m = 0;
  for (let V = i; V <= l; V++) {
    const Te = u.children?.[V];
    if (!Te)
      return e.removeSummary(n), null;
    const q = To(e.findEle(Te.id)), { offsetLeft: U, offsetTop: ke } = M(r, q), _e = i === l ? 10 : 20;
    V === i && (g = ke + _e), V === l && (m = ke + q.offsetHeight - _e), U < v && (v = U), q.offsetWidth + U > p && (p = q.offsetWidth + U);
  }
  let w, E;
  const N = u.parent ? 10 : 0, f = g + N, y = m + N, x = (f + y) / 2, S = c?.stroke || a.cssVar["--color"], C = c?.labelColor || a.cssVar["--color"], T = "s-" + n, D = e.markdown ? e.markdown(o, t) : o;
  b === H.LHS ? (w = ze(`M ${v + 10} ${f} c -5 0 -10 5 -10 10 L ${v} ${y - 10} c 0 5 5 10 10 10 M ${v} ${x} h -10`, S), E = de(D, v - 20, x, { anchor: "end", color: C, dataType: "summary", svgId: T })) : (w = ze(`M ${p - 10} ${f} c 5 0 10 5 10 10 L ${p} ${y - 10} c 0 5 -5 10 -10 10 M ${p} ${x} h 10`, S), E = de(D, p + 20, x, { anchor: "start", color: C, dataType: "summary", svgId: T }));
  const L = No(T);
  return L.appendChild(w), e.labelContainer.appendChild(E), re(E), L.summaryObj = t, L.labelEl = E, d.appendChild(L), L;
}, _o = function(e = {}) {
  if (!this.currentNodes) return;
  const { currentNodes: t, summaries: n, bus: o } = this, { parent: s, start: i, end: l } = So(t), c = { id: B(), parent: s, start: i, end: l, label: "summary", style: e.style }, r = Ne(this, c);
  n.push(c), this.editSummary(r), o.fire("operation", {
    name: "createSummary",
    obj: c
  });
}, Do = function(e) {
  const t = B(), n = { ...e, id: t };
  Ne(this, n), this.summaries.push(n), this.bus.fire("operation", {
    name: "createSummary",
    obj: n
  });
}, Lo = function(e) {
  const t = this.summaries.findIndex((n) => n.id === e);
  t > -1 && (this.summaries.splice(t, 1), this.nodes.querySelector("#s-" + e)?.remove(), this.nodes.querySelector("#label-s-" + e)?.remove()), this.bus.fire("operation", {
    name: "removeSummary",
    obj: { id: e }
  });
}, Mo = function(e) {
  const t = e.labelEl;
  t && t.classList.add("selected"), this.currentSummary = e, this.bus.fire("selectSummary", e.summaryObj);
}, Ao = function() {
  this.currentSummary?.labelEl?.classList.remove("selected"), this.currentSummary = null, this.bus.fire("unselectSummary");
}, Po = function() {
  this.summarySvg.innerHTML = "", this.summaries.forEach((e) => {
    try {
      Ne(this, e);
    } catch {
    }
  }), this.nodes.insertAdjacentElement("beforeend", this.summarySvg);
}, Oo = function(e) {
  e && e.labelEl && rt(this, e.labelEl, e.summaryObj);
}, Ho = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  createSummary: _o,
  createSummaryFrom: Do,
  editSummary: Oo,
  removeSummary: Lo,
  renderSummary: Po,
  selectSummary: Mo,
  unselectSummary: Ao
}, Symbol.toStringTag, { value: "Module" })), _ = "http://www.w3.org/2000/svg";
function $o(e, t) {
  const n = document.createElementNS(_, "svg");
  return k(n, {
    version: "1.1",
    xmlns: _,
    height: e,
    width: t
  }), n;
}
function jo(e, t) {
  return (parseInt(e) - parseInt(t)) / 2;
}
function Io(e, t, n, o) {
  const s = document.createElementNS(_, "g");
  let i = "";
  return e.text ? i = e.text.textContent : i = e.childNodes[0].textContent, i.split(`
`).forEach((c, r) => {
    const a = document.createElementNS(_, "text");
    k(a, {
      x: n + parseInt(t.paddingLeft) + "",
      y: o + parseInt(t.paddingTop) + jo(t.lineHeight, t.fontSize) * (r + 1) + parseFloat(t.fontSize) * (r + 1) + "",
      "text-anchor": "start",
      "font-family": t.fontFamily,
      "font-size": `${t.fontSize}`,
      "font-weight": `${t.fontWeight}`,
      fill: `${t.color}`
    }), a.innerHTML = c, s.appendChild(a);
  }), s;
}
function Ro(e, t, n, o) {
  let s = "";
  e.nodeObj?.dangerouslySetInnerHTML ? s = e.nodeObj.dangerouslySetInnerHTML : e.text ? s = e.text.textContent : s = e.childNodes[0].textContent;
  const i = document.createElementNS(_, "foreignObject");
  k(i, {
    x: n + parseInt(t.paddingLeft) + "",
    y: o + parseInt(t.paddingTop) + "",
    width: t.width,
    height: t.height
  });
  const l = document.createElement("div");
  return k(l, {
    xmlns: "http://www.w3.org/1999/xhtml",
    style: `font-family: ${t.fontFamily}; font-size: ${t.fontSize}; font-weight: ${t.fontWeight}; color: ${t.color}; white-space: pre-wrap;`
  }), l.innerHTML = s, i.appendChild(l), i;
}
function Bo(e, t) {
  const n = getComputedStyle(t), { offsetLeft: o, offsetTop: s } = M(e.nodes, t), i = document.createElementNS(_, "rect");
  return k(i, {
    x: o + "",
    y: s + "",
    rx: n.borderRadius,
    ry: n.borderRadius,
    width: n.width,
    height: n.height,
    fill: n.backgroundColor,
    stroke: n.borderColor,
    "stroke-width": n.borderWidth
  }), i;
}
function Q(e, t, n = !1) {
  const o = getComputedStyle(t), { offsetLeft: s, offsetTop: i } = M(e.nodes, t), l = document.createElementNS(_, "rect");
  k(l, {
    x: s + "",
    y: i + "",
    rx: o.borderRadius,
    ry: o.borderRadius,
    width: o.width,
    height: o.height,
    fill: o.backgroundColor,
    stroke: o.borderColor,
    "stroke-width": o.borderWidth
  });
  const c = document.createElementNS(_, "g");
  c.appendChild(l);
  let r;
  return n ? r = Ro(t, o, s, i) : r = Io(t, o, s, i), c.appendChild(r), c;
}
function Wo(e, t) {
  const n = getComputedStyle(t), { offsetLeft: o, offsetTop: s } = M(e.nodes, t), i = document.createElementNS(_, "a"), l = document.createElementNS(_, "text");
  return k(l, {
    x: o + "",
    y: s + parseInt(n.fontSize) + "",
    "text-anchor": "start",
    "font-family": n.fontFamily,
    "font-size": `${n.fontSize}`,
    "font-weight": `${n.fontWeight}`,
    fill: `${n.color}`
  }), l.innerHTML = t.textContent, i.appendChild(l), i.setAttribute("href", t.href), i;
}
function Yo(e, t) {
  const n = getComputedStyle(t), { offsetLeft: o, offsetTop: s } = M(e.nodes, t), i = document.createElementNS(_, "image");
  return k(i, {
    x: o + "",
    y: s + "",
    width: n.width + "",
    height: n.height + "",
    href: t.src
  }), i;
}
const ee = 100, Xo = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">', Fo = (e, t = !1) => {
  const n = e.nodes, o = n.offsetHeight + ee * 2, s = n.offsetWidth + ee * 2, i = $o(o + "px", s + "px"), l = document.createElementNS(_, "svg"), c = document.createElementNS(_, "rect");
  k(c, {
    x: "0",
    y: "0",
    width: `${s}`,
    height: `${o}`,
    fill: e.theme.cssVar["--bgcolor"]
  }), i.appendChild(c), n.querySelectorAll(".subLines").forEach((h) => {
    const u = h.cloneNode(!0), { offsetLeft: b, offsetTop: v } = M(n, h.parentElement);
    u.setAttribute("x", `${b}`), u.setAttribute("y", `${v}`), l.appendChild(u);
  });
  const r = n.querySelector(".lines")?.cloneNode(!0);
  r && l.appendChild(r);
  const a = n.querySelector(".topiclinks")?.cloneNode(!0);
  a && l.appendChild(a);
  const d = n.querySelector(".summary")?.cloneNode(!0);
  return d && l.appendChild(d), n.querySelectorAll("me-tpc").forEach((h) => {
    h.nodeObj.dangerouslySetInnerHTML ? l.appendChild(Q(e, h, !t)) : (l.appendChild(Bo(e, h)), l.appendChild(Q(e, h.text, !t)));
  }), n.querySelectorAll(".tags > span").forEach((h) => {
    l.appendChild(Q(e, h));
  }), n.querySelectorAll(".icons > span").forEach((h) => {
    l.appendChild(Q(e, h));
  }), n.querySelectorAll(".hyper-link").forEach((h) => {
    l.appendChild(Wo(e, h));
  }), n.querySelectorAll("img").forEach((h) => {
    l.appendChild(Yo(e, h));
  }), k(l, {
    x: ee + "",
    y: ee + "",
    overflow: "visible"
  }), i.appendChild(l), i;
}, Ko = (e, t) => (t && e.insertAdjacentHTML("afterbegin", "<style>" + t + "</style>"), Xo + e.outerHTML);
function Vo(e) {
  return new Promise((t, n) => {
    const o = new FileReader();
    o.onload = (s) => {
      t(s.target.result);
    }, o.onerror = (s) => {
      n(s);
    }, o.readAsDataURL(e);
  });
}
const zo = function(e = !1, t) {
  const n = Fo(this, e), o = Ko(n, t);
  return new Blob([o], { type: "image/svg+xml" });
}, Go = async function(e = !1, t) {
  const n = this.exportSvg(e, t), o = await Vo(n);
  return new Promise((s, i) => {
    const l = new Image();
    l.setAttribute("crossOrigin", "anonymous"), l.onload = () => {
      const c = document.createElement("canvas");
      c.width = l.width, c.height = l.height, c.getContext("2d").drawImage(l, 0, 0), c.toBlob(s, "image/png", 1);
    }, l.src = o, l.onerror = i;
  });
}, qo = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  exportPng: Go,
  exportSvg: zo
}, Symbol.toStringTag, { value: "Module" }));
function Uo(e, t) {
  return async function(...n) {
    const o = this.before[t];
    o && !await o.apply(this, n) || e.apply(this, n);
  };
}
const Ge = Object.keys(ot), gt = {};
for (let e = 0; e < Ge.length; e++) {
  const t = Ge[e];
  gt[t] = Uo(ot[t], t);
}
const Jo = {
  getObjById: ne,
  generateNewObj: mt,
  layout: Nt,
  linkDiv: In,
  editTopic: At,
  createWrapper: _t,
  createParent: Dt,
  createChildren: Lt,
  createTopic: Mt,
  findEle: Ze,
  changeTheme: lo,
  changeCompact: co,
  ...Sn,
  ...gt,
  ...Co,
  ...Ho,
  ...qo,
  init(e) {
    if (e = JSON.parse(JSON.stringify(e)), !e || !e.nodeData) return new Error("MindElixir: `data` is required");
    e.direction !== void 0 && (this.direction = e.direction), e.compact !== void 0 && (this.compact = e.compact), this.changeTheme(e.theme || this.theme, !1), e.meta && (this.meta = e.meta), this.nodeData = e.nodeData, R(this.nodeData), this.arrows = e.arrows || [], this.summaries = e.summaries || [], this.tidyArrow(), this.toolBar && Qn(this), this.keypress && On(this, this.keypress), ro(this), this.disposable.push(St()), this.contextMenu && this.disposable.push(Bn(this, this.contextMenu)), this.allowUndo && this.disposable.push(Yn(this)), this.layout(), this.linkDiv(), this.toCenter();
  },
  destroy() {
    this.disposable.forEach((e) => e()), this.el && (this.el.innerHTML = ""), this.el = void 0, this.nodeData = void 0, this.arrows = void 0, this.summaries = void 0, this.currentArrow = void 0, this.currentNodes = void 0, this.currentSummary = void 0, this.theme = void 0, this.direction = void 0, this.bus = void 0, this.container = void 0, this.map = void 0, this.lines = void 0, this.linkController = void 0, this.arrowSvg = void 0, this.P2 = void 0, this.P3 = void 0, this.line1 = void 0, this.line2 = void 0, this.nodes = void 0, this.selection?.destroy(), this.selection = void 0;
  },
  /**
   * @public
   * @param {boolean} enable
   */
  enableMobileMultiSelect(e) {
    this.mobileMultiSelect = e;
  }
}, Zo = "5.12.2";
function Qo(e) {
  return {
    x: 0,
    y: 0,
    moved: !1,
    // differentiate click and move
    mousedown: !1,
    handlePointerDown(t) {
      this.moved = !1;
      const n = t.target, o = e.mouseSelectionButton === 0 ? 2 : 0, s = e.spacePressed && t.button === 0 && t.pointerType === "mouse", i = !e.editable || t.button === o && t.pointerType === "mouse" || t.pointerType === "touch";
      !s && !i || (this.x = t.clientX, this.y = t.clientY, n.className !== "circle" && n.contentEditable !== "plaintext-only" && (this.mousedown = !0, n.setPointerCapture(t.pointerId)));
    },
    handlePointerMove(t) {
      if (!this.mousedown || t.target.contentEditable === "plaintext-only" && !e.spacePressed) return !1;
      const n = t.clientX - this.x, o = t.clientY - this.y;
      return this.x = t.clientX, this.y = t.clientY, this.moved = !0, e.move(n, o), !0;
    },
    handlePointerUp(t) {
      if (!this.mousedown) return;
      const n = t.target;
      n.hasPointerCapture && n.hasPointerCapture(t.pointerId) && n.releasePointerCapture(t.pointerId), this.mousedown = !1;
    },
    clear() {
      this.mousedown = !1, this.moved = !1;
    }
  };
}
function P({
  el: e,
  direction: t,
  editable: n,
  contextMenu: o,
  toolBar: s,
  keypress: i,
  mouseSelectionButton: l,
  selectionContainer: c,
  before: r,
  newTopicName: a,
  allowUndo: d,
  generateMainBranch: h,
  generateSubBranch: u,
  overflowHidden: b,
  compact: v,
  theme: p,
  alignment: g,
  scaleSensitivity: m,
  scaleMax: w,
  scaleMin: E,
  handleWheel: N,
  markdown: f,
  imageProxy: y,
  pasteHandler: x,
  mobileMultiSelect: S
}) {
  let C = null;
  const T = Object.prototype.toString.call(e);
  if (T === "[object HTMLDivElement]" ? C = e : T === "[object String]" && (C = document.querySelector(e)), !C) throw new Error("MindElixir: el is not a valid element");
  C.style.position = "relative", C.innerHTML = "", this.el = C, this.disposable = [], this.before = r || {}, this.newTopicName = a || "New Node", this.contextMenu = o ?? !0, this.toolBar = s ?? !0, this.keypress = i ?? !0, this.mouseSelectionButton = l ?? 0, this.direction = t ?? 1, this.editable = n ?? !0, this.allowUndo = d ?? !0, this.scaleSensitivity = m ?? 0.1, this.scaleMax = w ?? 1.4, this.scaleMin = E ?? 0.2, this.generateMainBranch = h || at, this.generateSubBranch = u || dt, this.overflowHidden = b ?? !1, this.compact = v ?? !1, this.alignment = g ?? "root", this.handleWheel = N ?? !0, this.markdown = f || void 0, this.imageProxy = y || void 0, this.currentNodes = [], this.currentArrow = null, this.scaleVal = 1, this.tempDirection = null, this.mobileMultiSelect = S ?? !1, this.panHelper = Qo(this), this.bus = $n(), this.container = document.createElement("div"), this.selectionContainer = c || this.container, this.container.className = "map-container";
  const D = window.matchMedia("(prefers-color-scheme: dark)");
  this.theme = p || (D.matches ? ue : fe);
  const L = document.createElement("div");
  L.className = "map-canvas", this.map = L, this.container.setAttribute("tabindex", "0"), this.container.appendChild(this.map), this.el.appendChild(this.container), this.nodes = document.createElement("me-nodes"), this.lines = z("lines"), this.summarySvg = z("summary"), this.linkController = z("linkcontroller"), this.P2 = document.createElement("div"), this.P3 = document.createElement("div"), this.P2.className = this.P3.className = "circle", this.P2.style.display = this.P3.style.display = "none", this.line1 = je(), this.line2 = je(), this.linkController.appendChild(this.line1), this.linkController.appendChild(this.line2), this.arrowSvg = z("topiclinks"), this.labelContainer = document.createElement("div"), this.labelContainer.className = "label-container", this.map.appendChild(this.nodes), this.overflowHidden ? this.container.style.overflow = "hidden" : this.disposable.push(Hn(this)), x && (this.pasteHandler = x);
}
P.prototype = Jo;
Object.defineProperty(P.prototype, "currentNode", {
  get() {
    return this.currentNodes[this.currentNodes.length - 1];
  },
  enumerable: !0
});
P.LEFT = 0;
P.RIGHT = 1;
P.SIDE = 2;
P.THEME = fe;
P.DARK_THEME = ue;
P.version = Zo;
P.E = Ze;
P.new = (e) => ({
  nodeData: {
    id: B(),
    topic: e || "new topic",
    children: []
  }
});
// Global exposure for non-module usage
window.MindElixir = P;
window.MindElixir.LEFT = es;
window.MindElixir.RIGHT = ts;
window.MindElixir.SIDE = ns;
window.MindElixir.THEME = fe;
window.MindElixir.DARK_THEME = ue;
window.MindElixir.version = Zo;

