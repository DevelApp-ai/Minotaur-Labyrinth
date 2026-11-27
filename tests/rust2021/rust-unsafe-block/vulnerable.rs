// CWE-133 unsafe block without invariant documentation
fn main() {
    unsafe {
        let p = std::ptr::null::<i32>();
        println!("{}", *p);
    }
}
