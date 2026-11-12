<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
          <template v-if="!hub.tool">
            <h1>Hub - {{activeName}}</h1>
            <p class="sub">Các công cụ đội ngũ của bạn đã xuất bản cho Agent của cộng đồng sử dụng: kịch bản các bước JSON hoặc script trong sandbox. Mọi bước chạy qua công cụ và khóa của bạn; người gọi chi trả chi phí các bước và mức giá bạn quy định.</p>
            <p v-if="hub.err" class="err">{{hub.err}}</p>
            <p v-if="hub.note" class="sub">{{hub.note}}</p>
            <div class="statgrid" style="margin:12px 0;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
              <div class="stat"><div class="n">{{hubLive()}}</div><div class="l">công cụ đang chạy</div></div>
              <div class="stat"><div class="n">{{money(hubEarned30())}}</div><div class="l">doanh thu 30 ngày</div></div>
              <div class="stat"><div class="n">{{hubRuns30()}}</div><div class="l">lượt chạy, 30 ngày</div></div>
              <div class="stat"><div class="n">{{hubFailing()}}</div><div class="l">gặp sự cố</div></div>
            </div>
            <p class="sub">Tạo mới từ terminal hoặc Agent của bạn: <code>treg hub init &lt;tên&gt; --script</code> · <code>hub_create</code> qua MCP.</p>
            <p v-if="hub.loading" class="sub">Đang tải…</p>
            <p v-else-if="!hubNewest().length" class="sub">Chưa có công cụ Hub nào.</p>
            <table v-else>
              <tr><th>Công cụ</th><th>Bản</th><th>Trạng thái</th><th>Loại</th><th>Giá cước</th><th>Tình trạng</th><th style="text-align:right">Chạy 30 ngày</th><th style="text-align:right">Doanh thu 30 ngày</th></tr>
              <tr v-for="t in hubNewest()" :key="t.tool_id" class="act-row" @click="openHubTool(t)">
                <td><b>{{t.tool_id}}</b><div class="muted" style="font-size:11px;max-width:52ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{t.summary}}</div></td>
                <td>{{t.version}}</td>
                <td><span :class="{ok:t.status==='live', warn:t.status==='failed', muted:t.status==='retired'}">{{t.status}}</span></td>
                <td>{{t.kind}}</td>
                <td :title="t.price_label">{{t.price_range||t.price_label||('$'+t.price_usd+'/run')}}<span v-if="t.price_samples" class="muted"> · {{t.price_samples}} {{t.price_samples===1?'lượt':'lượt'}}</span></td>
                <td><span :class="{ok:t.health==='ok', warn:t.health==='failing', muted:t.health==='unknown'}">{{t.health}}</span><span v-if="t.fails_in_a_row" class="muted"> · {{t.fails_in_a_row}} lần lỗi liên tiếp</span></td>
                <td style="text-align:right">{{t.runs_30d}}</td>
                <td style="text-align:right">{{money(t.earned_30d_micro)}}</td>
              </tr>
            </table>
          </template>

          <template v-else>
            <div style="margin-bottom:8px"><button class="btn sm" @click="closeHubTool()">← Tất cả công cụ</button></div>
            <h1>{{hub.tool.tool_id.split('.').slice(1).join('.')}} <span class="muted" style="font-size:13px">v{{hub.tool.version}} · {{hub.tool.status}} · {{hub.tool.kind}}</span></h1>
            <p class="sub" style="margin:0 0 8px"><code>{{hub.tool.tool_id}}</code> · <a :href="hubPage(hub.tool)" target="_blank" rel="noopener">trang công khai ↗</a></p>
            <p v-if="hub.err" class="err">{{hub.err}}</p>
            <p v-if="hub.note" class="sub">{{hub.note}}</p>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 4px">
              <button class="btn sm" @click="copyText(hubCallLine(hub.tool),'lệnh gọi')">Sao chép lệnh gọi</button>
              <button class="btn sm" @click="copyText(hubPage(hub.tool),'link chia sẻ')">Sao chép link chia sẻ</button>
              <button v-if="hub.tool.status==='live' && canRegister" class="btn sm" :class="{danger:hub.confirmRetire===hub.tool.tool_id}" @click="retireHubTool()">{{hub.confirmRetire===hub.tool.tool_id?'Xác nhận thu hồi':'Thu hồi công cụ'}}</button>
            </div>
            <div class="tabs" style="margin:10px 0 4px">
              <button :class="{active:hub.tab==='overview'}" @click="hub.tab='overview'">Tổng quan</button>
              <button :class="{active:hub.tab==='versions'}" @click="hub.tab='versions'">Phiên bản</button>
              <button :class="{active:hub.tab==='price'}" @click="hub.tab='price'">Giá cước</button>
              <button :class="{active:hub.tab==='listing'}" @click="hub.tab='listing'">Niêm yết</button>
              <button :class="{active:hub.tab==='earnings'}" @click="hub.tab='earnings'; loadHubEarnings()">Doanh thu</button>
              <button :class="{active:hub.tab==='runs'}" @click="hub.tab='runs'; loadHubHealth()">Lượt chạy &amp; Log</button>
              <button :class="{active:hub.tab==='health'}" @click="hub.tab='health'; loadHubHealth()">Tình trạng</button>
            </div>

            <template v-if="hub.tab==='overview'">
              <div class="statgrid" style="margin:12px 0;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
                <div class="stat"><div class="n">{{hubRunCost(hub.tool)}}</div><div class="l">{{hub.tool.price_samples ? 'chi phí người gọi trả (gồm phí + giá của bạn, '+hub.tool.price_samples+(hub.tool.price_samples===1?' lượt chạy gần đây)':' lượt chạy gần đây)') : 'chi phí người gọi trả (chưa có lượt chạy)'}}</div></div>
                <div class="stat"><div class="n sm">{{hub.tool.price_label}}</div><div class="l">giá của bạn</div></div>
                <div class="stat"><div class="n">{{hub.tool.runs_30d}}</div><div class="l">lượt chạy của người khác, 30 ngày</div></div>
                <div class="stat"><div class="n">{{money(hub.tool.earned_30d_micro)}}</div><div class="l">doanh thu, 30 ngày</div></div>
                <div class="stat"><div class="n">{{hub.tool.health}}</div><div class="l">tình trạng</div></div>
              </div>
              <div class="lbl">Tóm tắt <span class="muted">(thông tin Agent đọc đầu tiên)</span></div>
              <p class="sub">{{hub.tool.summary}}</p>
              <div class="lbl">Tham số đầu vào (Inputs)</div>
              <table><tr><th>Tên</th><th>Kiểu</th><th>Mặc định</th><th>Ghi chú</th></tr>
                <tr v-for="(v,k) in hub.tool.inputs" :key="k"><td><code>{{k}}</code></td><td>{{v.type}}<span v-if="v.max!==undefined"> ≤ {{v.max}}</span></td><td>{{v.default!==undefined?JSON.stringify(v.default):'bắt buộc'}}</td><td class="muted">{{v.note||''}}</td></tr>
              </table>
              <div class="lbl" style="margin-top:12px">Công cụ sử dụng <span class="muted">(chỉ bạn mới thấy)</span></div>
              <p class="sub"><code v-for="u in hub.tool.uses" :key="u" style="margin-right:8px">{{u}}</code></p>
              <div class="lbl">Đầu ra (Output)</div>
              <p class="sub"><code>{{(hub.tool.output&&hub.tool.output.fields)?hub.tool.output.fields.join(', '):Object.keys(hub.tool.output||{}).join(', ')}}</code></p>
              <template v-if="hub.tool.data"><div class="lbl">Dữ liệu</div>
              <p class="sub">{{hub.tool.data.rows.toLocaleString()}} dòng · {{(hub.tool.data.bytes/1024).toFixed(0)}} KB đã tải lên cùng phiên bản này</p></template>
              <div class="lbl">Cách gọi công cụ</div>
              <pre style="white-space:pre-wrap;word-break:break-all">{{hubCallLine(hub.tool)}}
POST {{proxy}}/call/{{hub.tool.tool_id}}    X-Treg-Token · JSON body of inputs</pre>
              <p class="sub">Tệp tin ở đây ở chế độ chỉ đọc; xuất bản phiên bản mới từ terminal (<code>treg hub publish .</code>) hoặc qua Agent (<code>hub_update</code>).</p>
            </template>

            <template v-if="hub.tab==='versions'">
              <p class="sub">Phiên bản đang chạy mới nhất sẽ phục vụ ID này. Người gọi có thể ghim phiên bản bằng <code>@N</code>; phiên bản cũ được ghim vẫn có thể gọi trong 30 ngày sau khi có bản mới.</p>
              <table><tr><th>Bản</th><th>Trạng thái</th><th>Xuất bản</th><th>Bởi</th><th>Kiểm tra</th><th>Tình trạng</th></tr>
                <tr v-for="v in hubVersions(hub.tool.tool_id)" :key="v.version"><td>{{v.version}}</td><td>{{v.status}}</td><td>{{(v.created_at||'').slice(0,16).replace('T',' ')}}</td><td>{{v.created_by}}</td>
                  <td>{{v.check_result?v.check_result.status:'-'}}<span v-if="v.check_result&&v.check_result.charged_micro" class="muted"> · {{v.check_result.charged_micro}} µ$</span></td><td>{{v.health}}</td></tr>
              </table>
            </template>

            <template v-if="hub.tab==='price'">
              <div class="statgrid" style="margin:12px 0;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))">
                <div class="stat"><div class="n sm">{{hub.tool.price_label}}</div><div class="l">giá của bạn</div></div>
                <div class="stat"><div class="n">{{hubRunCost(hub.tool)}}</div><div class="l">{{hub.tool.price_samples ? 'chi phí người gọi trả, '+hub.tool.price_samples+(hub.tool.price_samples===1?' lượt gần đây':' lượt gần đây') : 'chưa có lượt chạy'}}</div></div>
              </div>
              <p class="sub">{{hubPriceExplain(hub.tool)}} Phí của nhà cung cấp (các bước trong catalog) được tính vào người gọi theo giá gốc; bạn không phải trả bất kỳ khoản phí nào. Tiền thu được sẽ cộng trực tiếp vào số dư của bạn ngay lập tức.</p>
              <div class="lbl">Khối định giá trong recipe.json <span class="muted">(phiên bản {{hub.tool.version}})</span></div>
              <pre style="white-space:pre-wrap">{{JSON.stringify(hub.tool.pricing||{}, null, 2)}}</pre>
              <div class="lbl" style="margin-top:12px">Thay đổi giá</div>
              <p class="sub">Yêu cầu Agent của bạn: nó sẽ chỉnh sửa khối <span class="mono">pricing</span> và xuất bản phiên bản mới, có hiệu lực ngay khi vượt qua bước kiểm tra.</p>
              <pre style="white-space:pre-wrap">{{hubPricePrompt(hub.tool)}}</pre>
              <button class="btn primary sm" @click="copyText(hubPricePrompt(hub.tool),'prompt')">Sao chép prompt cho Agent của bạn</button>
            </template>

            <template v-if="hub.tab==='listing'">
              <p class="sub">Các lựa chọn ở đây không làm tăng số phiên bản. Khi đã được niêm yết, mỗi phiên bản mới hoặc thay đổi giá sẽ cần được treg duyệt lại.</p>
              <div style="margin:14px 0 4px">
                <div class="lbl">Trong tìm kiếm danh mục (Catalog search)</div>
                <p class="sub" style="margin:4px 0;max-width:70ch">
                  <b :class="{ok:hubListing(hub.tool)==='approved', warn:hubListing(hub.tool)==='rejected'}">{{hubListingWords(hub.tool)}}</b>
                  <template v-if="hubListing(hub.tool)==='rejected' && hub.tool.listing.reason"> Lý do: {{hub.tool.listing.reason}}</template>
                  <template v-if="hubListing(hub.tool)==='requested' && hub.tool.listing.reason"> Lần từ chối trước: {{hub.tool.listing.reason}}</template>
                </p>
                <button v-if="['none','rejected','unlisted'].includes(hubListing(hub.tool))" class="btn sm primary" :disabled="hub.flagSaving||!canRegister||hub.tool.status!=='live'" @click="setHubFlag('listed',true)">{{hubListing(hub.tool)==='rejected'?'Yêu cầu lại':hubListing(hub.tool)==='unlisted'?'Niêm yết lại':'Yêu cầu niêm yết'}}</button>
                <button v-else class="btn sm" :disabled="hub.flagSaving||!canRegister" @click="setHubFlag('listed',false)">{{hubListing(hub.tool)==='approved'?'Hủy niêm yết':'Rút lại yêu cầu'}}</button>
                <p class="sub" style="margin:6px 0 0;max-width:70ch">Đã niêm yết: công cụ sẽ xuất hiện trong tìm kiếm danh mục, được đánh dấu là công cụ Hub của đội ngũ bạn. Chưa niêm yết: chỉ những ai có ID hoặc liên kết chia sẻ mới có thể gọi.</p>
              </div>
              <div style="margin:14px 0 4px">
                <label class="tgl" style="font-size:13.5px"><input type="checkbox" :checked="hub.tool.public_log!==false" :disabled="hub.flagSaving||!canRegister||hub.tool.status!=='live'" @change="setHubFlag('public_log',$event.target.checked)"/><span><b>Công khai nhật ký chạy trên trang chia sẻ</b></span></label>
                <p class="sub" style="margin:4px 0 0 21px;max-width:70ch">Hiển thị 20 lượt chạy gần nhất và số lượt mỗi ngày trong 30 ngày: thời gian, kết quả, thời lượng và giá đã trả. Không bao giờ lộ người gọi, tham số hay kết quả chi tiết.</p>
              </div>
            </template>

            <template v-if="hub.tab==='earnings'">
              <p v-if="!hub.earnings" class="sub">Đang tải…</p>
              <template v-else>
                <div class="statgrid" style="margin:12px 0;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
                  <div class="stat"><div class="n">{{money(hub.earnings.earned_micro)}}</div><div class="l">doanh thu 90 ngày</div></div>
                  <div class="stat"><div class="n">{{hub.earnings.runs}}</div><div class="l">lượt chạy của người khác</div></div>
                  <div class="stat"><div class="n">{{hub.earnings.by_day.reduce((a,d)=>a+d.ok,0)}} / {{hub.earnings.by_day.reduce((a,d)=>a+d.failed,0)}}</div><div class="l">thành công / lỗi</div></div>
                </div>
                <p class="sub"><a :href="'/hub/tools/'+encodeURIComponent(hub.tool.tool_id)+'/earnings?days=90&format=csv'" target="_blank">Tải file CSV</a> · chỉ gồm số lượt và số tiền; không bao gồm danh tính người gọi.</p>
                <table><tr><th>Ngày</th><th style="text-align:right">Lượt chạy</th><th style="text-align:right">Thành công</th><th style="text-align:right">Lỗi</th><th style="text-align:right">Doanh thu</th></tr>
                  <tr v-for="d in hub.earnings.by_day" :key="d.day"><td>{{d.day}}</td><td style="text-align:right">{{d.runs}}</td><td style="text-align:right">{{d.ok}}</td><td style="text-align:right">{{d.failed}}</td><td style="text-align:right">{{money(d.earned_micro)}}</td></tr>
                </table>
              </template>
            </template>

            <template v-if="hub.tab==='runs'">
              <p class="sub">Các lượt chạy gần nhất của phiên bản này. Bạn thấy đầy đủ dòng log của script và chi tiết lỗi; người gọi chỉ thấy vết thực thi của họ.</p>
              <p v-if="!hub.health" class="sub">Đang tải…</p>
              <table v-else><tr><th>Thời gian</th><th>Mã chạy</th><th>Loại</th><th>Trạng thái</th><th style="text-align:right">Số bước</th><th style="text-align:right">Phí bước</th><th style="text-align:right">Giá cước</th><th style="text-align:right">ms</th></tr>
                <template v-for="r in hub.health.runs" :key="r.run_id">
                  <tr class="act-row" @click="toggleHubRun(r)"><td>{{(r.at||'').slice(5,16).replace('T',' ')}}</td><td><code>{{r.run_id.slice(0,10)}}…</code></td><td>{{r.kind}}</td><td><span :class="{ok:r.status==='ok', warn:r.status!=='ok'}">{{r.status}}</span><span v-if="r.error" class="muted"> · {{r.error}}</span></td><td style="text-align:right">{{r.steps}}</td><td style="text-align:right">{{r.cost_micro}} µ$</td><td style="text-align:right">{{money(r.price_micro)}}</td><td style="text-align:right">{{r.ms}}</td></tr>
                  <tr v-if="hub.runOpen===r.run_id"><td colspan="8">
                    <div v-if="!r.detail" class="muted">Đang tải…</div>
                    <div v-else style="font-size:12px;line-height:1.6">
                      <div><span class="muted">đầu vào</span> <code>{{JSON.stringify(r.detail.inputs)}}</code></div>
                      <div v-for="(s,i) in (r.detail.trace||[])" :key="i"><span class="muted">vết</span> wave {{s.wave}} · {{s.name}} · <code>{{s.call}}</code> · {{s.outcome}} {{s.status||''}} · {{s.cost_micro}} µ$ · {{s.key||''}} key · {{s.ms}} ms<span v-if="s.error" class="warn"> · {{String(s.error).slice(0,300)}}</span></div>
                      <div v-for="(l,i) in (r.detail.log||[])" :key="'l'+i"><span class="muted">nhật ký</span> {{l}}</div>
                      <div v-if="r.detail.error&&r.detail.error.message"><span class="muted">lỗi</span> {{r.detail.error.error||''}} {{r.detail.error.message}}</div>
                    </div>
                  </td></tr>
                </template>
              </table>
            </template>

            <template v-if="hub.tab==='health'">
              <p v-if="!hub.health" class="sub">Đang tải…</p>
              <template v-else>
                <div class="card" style="max-width:640px"><b :class="{ok:hub.health.health==='ok', warn:hub.health.health==='failing'}">{{hub.health.health}}</b>
                  <span class="muted"> · {{hub.health.fails_in_a_row}} lần lỗi liên tiếp · lần chạy cuối {{(hub.health.last_run_at||'-').slice(0,16).replace('T',' ')}}</span>
                  <div v-if="hub.health.last_check" class="sub" style="margin-top:6px">lần kiểm tra cuối: {{hub.health.last_check.status}}<span v-if="hub.health.last_check.scheduled"> (định kỳ)</span> lúc {{(hub.health.last_check.checked_at||'').slice(0,16).replace('T',' ')}}<span v-if="hub.health.last_check.error"> · {{hub.health.last_check.error.error||''}} {{hub.health.last_check.error.message||''}}</span></div>
                </div>
                <p class="sub" style="margin-top:10px">Một công cụ bị đánh dấu là <b>gặp sự cố (failing)</b> sau 3 lần chạy thất bại liên tiếp (lượt gọi thực tế hoặc lượt kiểm tra tự động định kỳ). Nó vẫn có thể gọi được; trang công khai sẽ hiển thị trạng thái này.</p>
              </template>
            </template>
          </template>
</template>

<style scoped>
/* the hub's state words (live / failing / an error line), on these pages only */
.ok{color:var(--green)} .warn{color:var(--amber)} p.err{color:var(--red)}
</style>
