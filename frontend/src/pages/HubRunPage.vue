<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
          <div style="margin-bottom:8px"><button class="btn sm" @click="go('hub')">← Hub</button></div>
          <p v-if="run.loading" class="sub">Đang tải…</p>
          <p v-else-if="run.err" class="err">{{run.err}}</p>
          <template v-else-if="run.data">
            <h1>Lượt chạy <code style="font-size:16px">{{run.data.run_id.slice(0,12)}}…</code> <span :class="{ok:run.data.status==='ok', warn:run.data.status!=='ok'}" style="font-size:13px">{{run.data.status}}</span></h1>
            <p class="sub"><code>{{run.data.tool_id}}@{{run.data.version}}</code> · {{(run.data.started_at||'').slice(0,19).replace('T',' ')}} · {{run.data.kind}} · bạn là {{run.data.you_are==='caller'?'người gọi':'người tạo'}}</p>
            <div class="statgrid" style="margin:12px 0;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
              <div class="stat"><div class="n">{{money(run.data.usage.cost_micro)}}</div><div class="l">{{run.data.you_are==='caller'?'bạn đã trả':'người gọi đã trả'}}</div></div>
              <div class="stat"><div class="n">{{money(run.data.usage.price_micro)}} + {{money(run.data.usage.steps_micro)}}</div><div class="l">giá người bán + các bước</div></div>
              <div class="stat"><div class="n">{{run.data.steps}}</div><div class="l">số bước</div></div>
              <div class="stat"><div class="n">{{fmtMs(run.data.duration_ms)}}</div><div class="l">thời lượng</div></div>
            </div>
            <div class="lbl">Tham số đầu vào (Inputs)</div>
            <pre style="white-space:pre-wrap;word-break:break-all">{{JSON.stringify(run.data.inputs, null, 2)}}</pre>
            <div class="lbl">Vết thực thi (Trace)</div>
            <table><tr><th>Wave</th><th>Bước</th><th>Lệnh gọi</th><th>Kết quả</th><th>Khóa</th><th style="text-align:right">Chi phí</th><th style="text-align:right">ms</th></tr>
              <tr v-for="(s,i) in run.data.trace" :key="i"><td>{{s.wave}}</td><td>{{s.name}}<span v-if="s.item!==undefined" class="muted">[{{s.item}}]</span></td><td><code>{{run.data.you_are==='maker'?s.call:(String(s.call).split('/')[0].includes('.')?'công cụ catalog':'công cụ của người tạo')}}</code></td><td><span :class="{ok:s.outcome==='ok', warn:s.outcome==='failed'}">{{s.outcome}}</span> {{s.status||''}}</td><td>{{s.key==='team'?'người tạo':(s.key||'')}}</td><td style="text-align:right">{{s.cost_micro}} µ$</td><td style="text-align:right">{{s.ms}}</td></tr>
              <tr v-if="run.data.usage.price_micro"><td>—</td><td>giá</td><td>cho người tạo</td><td><span class="ok">đã quyết toán</span></td><td></td><td style="text-align:right">{{run.data.usage.price_micro}} µ$</td><td></td></tr>
            </table>
            <p v-if="run.data.you_are==='caller'" class="sub">Lượt chạy thất bại sẽ hiển thị tên và trạng thái của bước lỗi, không hiển thị URL upstream hoặc nội dung lỗi bảo mật.</p>
            <template v-if="run.data.error">
              <div class="lbl">Chi tiết lỗi</div>
              <pre style="white-space:pre-wrap;word-break:break-all">{{run.data.error.error||''}} {{run.data.error.step?('· bước '+run.data.error.step):''}} {{run.data.error.message||''}}</pre>
            </template>
            <template v-if="run.data.log&&run.data.log.length">
              <div class="lbl">Nhật ký <span class="muted">(dòng log của script; chỉ người tạo mới thấy)</span></div>
              <pre style="white-space:pre-wrap;word-break:break-all">{{run.data.log.join('\n')}}</pre>
            </template>
            <template v-if="run.data.output!==undefined && run.data.output!==null">
              <div class="lbl">Dữ liệu đầu ra (Output)</div>
              <pre style="white-space:pre-wrap;word-break:break-all;max-height:480px;overflow:auto">{{JSON.stringify(run.data.output, null, 2)}}</pre>
            </template>
          </template>
</template>

<style scoped>
/* the hub's state words (live / failing / an error line), on these pages only */
.ok{color:var(--green)} .warn{color:var(--amber)} p.err{color:var(--red)}
</style>
