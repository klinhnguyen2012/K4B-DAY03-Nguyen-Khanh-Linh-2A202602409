import { useState } from "react";

const cards = [
  { id: "HB_TEST_01", name: "Technology Excellence Scholarship", school: "Đại học Công nghệ Mẫu · Việt Nam", funding: "75% học phí", deadline: "31 Jan 2027", need: "Cần IELTS 6.5", status: "Phù hợp nhất" },
  { id: "HB_TEST_02", name: "Global Computing Scholarship", school: "International Sample University · Úc", funding: "Toàn phần", deadline: "15 Dec 2026", need: "Cần GPA 3.6 · IELTS 7.0", status: "Mục tiêu dài hạn" },
];
const tasks = ["Xác nhận GPA theo thang điểm 4.0", "Đăng ký thi IELTS 6.5", "Hoàn thiện CV và bảng điểm", "Viết bài luận học bổng", "Xin hai thư giới thiệu"];
const start = [
  ["user", "Em có GPA 3.5/4.0, IELTS 6.0 và muốn học Thạc sĩ CNTT kỳ 2027. Hãy tìm học bổng phù hợp."],
  ["agent", "Tìm thấy 2 lựa chọn thử nghiệm. HB_TEST_01 phù hợp với GPA hiện tại, còn thiếu IELTS 6.5. Mình đã đặt các mốc chuẩn bị theo deadline 31/01/2027."],
];
function reply(text) {
  const value = text.toLowerCase();
  if (value.includes("hồ sơ") || value.includes("sv2026001")) return "Hồ sơ hiện có: GPA 3.5/4.0, IELTS 6.0, hoạt động Câu lạc bộ Công nghệ, mục tiêu Thạc sĩ CNTT kỳ 2027.";
  if (value.includes("kế hoạch") || value.includes("checklist")) return "Kế hoạch HB_TEST_01: nâng IELTS trước 30/11/2026, hoàn thiện hồ sơ trước 20/12/2026, xin thư giới thiệu trước 10/01/2027.";
  return "Mình sẽ dùng hồ sơ, ngành học, kỳ nhập học, khu vực ưu tiên và nhu cầu tài chính để tìm lựa chọn phù hợp.";
}
export function App() {
  const [selected, setSelected] = useState("HB_TEST_01");
  const [messages, setMessages] = useState(start);
  const [input, setInput] = useState("");
  const [done, setDone] = useState([false, false, false, false, false]);
  const submit = (event) => { event.preventDefault(); const text = input.trim(); if (!text) return; setMessages((m) => [...m, ["user", text]]); setInput(""); setTimeout(() => setMessages((m) => [...m, ["agent", reply(text)]]), 360); };
  return <main className="experience"><section className="frame">
    <header><button className="brand"><b>S</b> ScholarAI</button><nav><button className="active">Khám phá</button><button>Hồ sơ</button><button>Kế hoạch</button></nav><span className="person"><i>KL</i> Khánh Linh</span></header>
    <section className="hero"><div><p className="eyebrow">Scholarship planning agent</p><h1>Đưa hồ sơ của bạn đến đúng cánh cửa.</h1><p>Tìm học bổng, nhận biết khoảng thiếu và biến deadline thành một kế hoạch rõ ràng.</p><div className="actions"><button onClick={() => document.querySelector("#results")?.scrollIntoView({behavior:"smooth"})}>Khám phá học bổng</button><button className="soft">Xem hồ sơ</button></div></div><div className="art" role="img" aria-label="Minh họa hành trình săn học bổng" /></section>
    <section className="grid"><aside className="box profile"><p className="eyebrow">Hồ sơ của bạn</p><h2>Nguyễn Khánh Linh</h2><small>Thạc sĩ CNTT · Kỳ 2027</small><div className="stats"><b>3.5<small>GPA / 4.0</small></b><b>6.0<small>IELTS</small></b><b>01<small>Hoạt động</small></b></div><p>Có nền tảng tốt cho HB_TEST_01. Ưu tiên nâng IELTS để tăng mức phù hợp.</p><button className="link">Cập nhật hồ sơ</button></aside>
      <section className="box chat"><div className="title"><div><p className="eyebrow">Trợ lý đang hoạt động</p><h2>Gợi ý từ hồ sơ</h2></div><span>Mock mode</span></div><div className="messages" aria-live="polite">{messages.map(([role,text],i)=><article key={i} className={role}>{text}</article>)}</div><form onSubmit={submit}><label className="sr" htmlFor="ask">Hỏi Scholarship Planning Agent</label><input id="ask" value={input} onChange={e=>setInput(e.target.value)} placeholder="Hỏi về hồ sơ hoặc học bổng..."/><button>Gửi</button></form></section>
      <aside className="box plan"><div className="title"><div><p className="eyebrow">Kế hoạch cá nhân</p><h2>{selected}</h2></div><strong>31 Jan</strong></div><ol>{[["Nâng IELTS","30 Nov 2026"],["CV & bài luận","20 Dec 2026"],["Thư giới thiệu","10 Jan 2027"],["Nộp hồ sơ","24 Jan 2027"]].map(([a,b],i)=><li key={a}><em>{i+1}</em><div><b>{a}</b><small>{b}</small></div></li>)}</ol><div className="progress"><span style={{width:`${done.filter(Boolean).length*20}%`}}/></div><small>{done.filter(Boolean).length}/5 công việc đã hoàn thành</small></aside></section>
    <section className="results" id="results"><div className="heading"><div><p className="eyebrow">Danh sách phù hợp</p><h2>Học bổng nên ưu tiên</h2></div><small>Dữ liệu thử nghiệm</small></div><div className="cards">{cards.map(c=><article className={selected===c.id?"card selected":"card"} key={c.id}><div><small>{c.status}</small><small>{c.deadline}</small></div><h3>{c.name}</h3><p>{c.school}</p><b>{c.funding}</b><span>{c.need}</span><button className="link" onClick={()=>setSelected(c.id)}>Chọn kế hoạch</button></article>)}<article className="check"><p className="eyebrow">Checklist</p><h3>Việc cần chuẩn bị</h3>{tasks.map((task,i)=><label key={task}><input type="checkbox" checked={done[i]} onChange={()=>setDone(d=>d.map((x,j)=>j===i?!x:x))}/>{task}</label>)}</article></div></section>
  </section></main>;
}
