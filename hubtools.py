import imgui
from place.ref import Ref
class HubTools:
    def __init__(self,editor):
        self.troubleshoot = False
        self.show_hub = False
        self.show_palette = False
        self.editor = editor
    def menu(self):
        if imgui.button("Quick Fix Areas"):
            self.troubleshoot = True
            self.fix_areadata(self.editor.level)
    def show(self):
        if self.troubleshoot:
            # Check all things in area_data
            _, self.troubleshoot = imgui.begin("!!!", closable=True)
            imgui.bullet_text("Remember to save!")
            imgui.end()
    def hideBlocks(self):
        if self.troubleshoot and not self.show_hub: return True
    def hidePalette(self):
        if self.troubleshoot and not self.show_palette: return True
    def fix_areadata(self, level):
        refs = []
        for block in level.blocks.values():
            for child in block.children:
                if type(child)==Ref:
                    refs.append(child)
        # Keyed list of refs
        krefs = {}
        # Keyed list of refs with area name (first found)
        valid = {}        
        for ref in refs:
            if ref.id not in krefs:
                krefs[ref.id] = [ref]
            else:
                krefs[ref.id].append(ref)
            if ref.area_name != None and ref.area_name != "" and ref.area_name != "_" and ref.id not in valid:
                 valid[ref.id]=ref
        for id in krefs:
            name = "__"
            if id in valid:
                name = valid[id].area_name
            for ref in krefs[id]:
                ref.area_name = name
        return krefs
    def area_manager(self):
        krefs = self.fix_areadata(self.editor.level)
        
        
                
                
        