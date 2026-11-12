<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="run-tool-dialog-title" aria-modal="true" v-dialog="() => { tryTool=null }" @click.self="tryTool=null" style="place-items:stretch;justify-items:end">
      <div class="drawer"><div class="hd" style="padding:15px 18px;border-bottom:1px solid var(--line)"><b id="run-tool-dialog-title">Sử dụng “{{tryTool.name}}”</b><button class="btn sm" @click="tryTool=null" aria-label="Đóng">✕</button></div>
        <div style="padding:16px 18px;overflow:auto">
          <template v-if="useMode==='call'">
            <p class="explain">Nhập đường dẫn API cho <span class="mono">{{tryTool.host}}</span> (phần sau tên miền) và nhấn Gửi — yêu cầu sẽ chạy qua proxy với khóa được tự động chèn. Bạn không cần tự gửi khóa.</p>
            <div v-if="tryTool.examples && tryTool.examples.length">
              <div class="lbl">Ví dụ — nhấp để điền nhanh</div>
              <div class="exrow"><span v-for="(ex,exi) in tryTool.examples" :key="exi" class="exchip" :class="{on:tryPath===ex.path}" @click="tryPath=ex.path; tryMethod=ex.method||'GET'"><span class="m">{{ex.method||'GET'}}</span>{{ex.note||ex.path}}</span></div>
            </div>
            <div class="field"><select v-model="tryMethod"><option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option></select><input v-model="tryPath" placeholder="đường dẫn, ví dụ: me" @keyup.enter="runTry"/></div>
            <textarea v-if="tryMethod!=='GET'" v-model="tryBody" placeholder='Nội dung yêu cầu body (ví dụ: {"key":"value"})' rows="3" style="width:100%;margin-top:8px;background:var(--bg);border:1px solid var(--line);color:var(--ink);border-radius:var(--rb);padding:8px;font-family:var(--mono);font-size:12.5px"></textarea>
            <div class="muted" style="font-size:12px;margin:6px 0 12px">→ {{tryMethod}} {{tryTool.base_url}}/{{tryPath}}</div>
            <button class="btn primary" @click="runTry" :disabled="trying">{{trying ? 'Đang gửi…' : '▶ Gửi yêu cầu'}}</button>
            <div v-if="tryResp!==null" style="margin-top:14px"><div class="muted" style="font-size:12px;margin-bottom:6px">Phản hồi <span class="badge" :class="(tryStatus>0&&tryStatus<400)?'ok':'invalid'">{{tryStatus||'LỖI'}}</span> · {{tryMs}}ms · khóa được chèn tự động bởi hệ thống</div><pre>{{tryResp}}</pre></div>
          </template>

          <template v-if="useMode==='run'">
            <p class="explain"><span class="mono">{{(tryTool.cli&&tryTool.cli.bin)||tryTool.name}}</span> là công cụ dòng lệnh (CLI), do đó chạy trực tiếp trên máy tính của bạn. Treg sẽ chèn thông tin xác thực cho phiên chạy này; lệnh không chạy trên máy chủ.</p>
            <pre>treg run {{tryTool.name}} -- &lt;args&gt;</pre>
            <p v-if="tryTool.cli && !tryTool.cli.enabled" class="explain">Quản trị viên đã tắt quyền chạy cục bộ cho công cụ này.</p>
          </template>
        </div></div>
    </div>
</template>
